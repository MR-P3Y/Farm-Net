import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_repository.dart';
import 'consultant_request_state.dart';

final consultantRequestControllerProvider =
    StateNotifierProvider<ConsultantRequestController, ConsultantRequestState>((
      ref,
    ) {
      return ConsultantRequestController(
        repository: ref.watch(consultantRepositoryProvider),
      );
    });

class ConsultantRequestController
    extends StateNotifier<ConsultantRequestState> {
  ConsultantRequestController({required ConsultantRepository repository})
    : _repository = repository,
      super(ConsultantRequestState.initial());

  final ConsultantRepository _repository;

  Future<bool> createRequest({
    required int consultantProfileId,
    required int? specialtyId,
    required String title,
    required String description,
    required String contactMethod,
  }) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      await _repository.createRequest(
        consultantProfileId: consultantProfileId,
        specialtyId: specialtyId,
        title: title,
        description: description,
        contactMethod: contactMethod,
      );

      state = state.copyWith(
        isSaving: false,
        successMessage: 'درخواست مشاوره ثبت شد.',
      );
      return true;
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ثبت درخواست مشاوره ناموفق بود.',
      );
      return false;
    }
  }

  Future<void> loadMyRequests() async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final requests = await _repository.myRequests();
      state = state.copyWith(isLoading: false, requests: requests);
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت درخواست‌های مشاوره ناموفق بود.',
      );
    }
  }

  Future<void> cancelRequest(int requestId) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      await _repository.cancelRequest(requestId: requestId);
      final requests = await _repository.myRequests();

      state = state.copyWith(
        isSaving: false,
        requests: requests,
        successMessage: 'درخواست مشاوره لغو شد.',
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'لغو درخواست مشاوره ناموفق بود.',
      );
    }
  }
}
