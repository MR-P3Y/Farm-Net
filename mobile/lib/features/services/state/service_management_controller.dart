import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/service_api.dart';
import '../data/service_models.dart';
import '../data/service_repository.dart';

class ServiceManagementState {
  const ServiceManagementState({
    this.isLoading = false,
    this.isSaving = false,
    this.profile,
    this.offers = const [],
    this.categories = const [],
    this.errorMessage,
    this.successMessage,
  });
  final bool isLoading;
  final bool isSaving;
  final ServiceProviderProfileOwner? profile;
  final List<ServiceOfferOwner> offers;
  final List<ServiceCategory> categories;
  final String? errorMessage;
  final String? successMessage;
  ServiceManagementState copyWith({
    bool? isLoading,
    bool? isSaving,
    ServiceProviderProfileOwner? profile,
    List<ServiceOfferOwner>? offers,
    List<ServiceCategory>? categories,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) => ServiceManagementState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    profile: profile ?? this.profile,
    offers: offers ?? this.offers,
    categories: categories ?? this.categories,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}

final serviceManagementProvider =
    StateNotifierProvider<ServiceManagementController, ServiceManagementState>(
      (ref) => ServiceManagementController(
        repository: ref.watch(serviceRepositoryProvider),
      ),
    );

class ServiceManagementController
    extends StateNotifier<ServiceManagementState> {
  ServiceManagementController({required ServiceRepository repository})
    : _repository = repository,
      super(const ServiceManagementState());
  final ServiceRepository _repository;

  Future<void> loadProfile() async => _runLoad(() async {
    final categories = await _repository.categories();
    final profile = await _repository.myProviderProfile();
    state = state.copyWith(
      isLoading: false,
      categories: categories,
      profile: profile,
    );
  });

  Future<bool> saveProfile(ServiceProviderProfileInput input) async =>
      _runSave(() async {
        final profile = await _repository.saveProviderProfile(
          input,
          create: state.profile == null,
        );
        state = state.copyWith(
          isSaving: false,
          profile: profile,
          successMessage: 'پروفایل ذخیره شد.',
        );
      });

  Future<bool> submitProfile() async => _runSave(() async {
    final profile = await _repository.submitProviderProfile();
    state = state.copyWith(
      isSaving: false,
      profile: profile,
      successMessage: 'پروفایل برای بررسی ارسال شد.',
    );
  });

  Future<void> loadOffers() async => _runLoad(() async {
    final categories = await _repository.categories();
    final offers = await _repository.myOffers();
    state = state.copyWith(
      isLoading: false,
      categories: categories,
      offers: offers,
    );
  });

  Future<ServiceOfferOwner?> saveOffer(
    ServiceOfferInput input, {
    int? offerId,
  }) async {
    ServiceOfferOwner? result;
    final ok = await _runSave(() async {
      result = await _repository.saveOffer(input, offerId: offerId);
      final offers = await _repository.myOffers();
      state = state.copyWith(
        isSaving: false,
        offers: offers,
        successMessage: 'خدمت ذخیره شد.',
      );
    });
    return ok ? result : null;
  }

  Future<bool> submitOffer(int id) => _runSave(() async {
    await _repository.submitOffer(id);
    final offers = await _repository.myOffers();
    state = state.copyWith(
      isSaving: false,
      offers: offers,
      successMessage: 'خدمت برای بررسی ارسال شد.',
    );
  });

  Future<void> _runLoad(Future<void> Function() action) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      await action();
    } on ServiceApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت اطلاعات ناموفق بود.',
      );
    }
  }

  Future<bool> _runSave(Future<void> Function() action) async {
    if (state.isSaving) return false;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      await action();
      return true;
    } on ServiceApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ذخیره اطلاعات ناموفق بود.',
      );
      return false;
    }
  }
}
