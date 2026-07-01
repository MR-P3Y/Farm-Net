import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_models.dart';
import '../data/consultant_repository.dart';
import 'consultant_profile_state.dart';

final consultantProfileControllerProvider =
    StateNotifierProvider<ConsultantProfileController, ConsultantProfileState>((
      ref,
    ) {
      return ConsultantProfileController(
        repository: ref.watch(consultantRepositoryProvider),
      );
    });

class ConsultantProfileController
    extends StateNotifier<ConsultantProfileState> {
  ConsultantProfileController({required ConsultantRepository repository})
    : _repository = repository,
      super(ConsultantProfileState.initial());

  final ConsultantRepository _repository;

  Future<void> load() async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final specialtiesFuture = _repository.specialties();
      final profileFuture = _repository.myProfile();

      final specialties = await specialtiesFuture;
      final profile = await profileFuture;

      state = state.copyWith(
        isLoading: false,
        specialties: specialties,
        profile: profile,
        clearProfile: profile == null,
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت پروفایل مشاور ناموفق بود.',
      );
    }
  }

  Future<bool> save(ConsultantProfileInput input) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final profile = await _repository.saveMyProfile(
        input: input,
        create: state.profile == null,
      );

      state = state.copyWith(
        isSaving: false,
        profile: profile,
        successMessage: 'پروفایل مشاور ذخیره شد.',
      );
      return true;
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ذخیره پروفایل مشاور ناموفق بود.',
      );
      return false;
    }
  }

  Future<bool> submit() async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final profile = await _repository.submitMyProfile();

      state = state.copyWith(
        isSaving: false,
        profile: profile,
        successMessage: 'پروفایل مشاور برای بررسی ارسال شد.',
      );
      return true;
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ارسال پروفایل برای بررسی ناموفق بود.',
      );
      return false;
    }
  }
}
