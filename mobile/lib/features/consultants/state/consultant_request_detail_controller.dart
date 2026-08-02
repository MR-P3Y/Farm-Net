import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_repository.dart';
import 'consultant_request_detail_state.dart';

final consultantRequestDetailControllerProvider = StateNotifierProvider<
  ConsultantRequestDetailController,
  ConsultantRequestDetailState
>((ref) {
  return ConsultantRequestDetailController(
    repository: ref.watch(consultantRepositoryProvider),
  );
});

class ConsultantRequestDetailController
    extends StateNotifier<ConsultantRequestDetailState> {
  ConsultantRequestDetailController({required ConsultantRepository repository})
    : _repository = repository,
      super(ConsultantRequestDetailState.initial());

  final ConsultantRepository _repository;

  Future<void> load({required int requestId, required bool assigned}) async {
    state = state.copyWith(
      isLoading: true,
      clearRequest: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final request =
          assigned
              ? await _repository.assignedRequestDetail(requestId)
              : await _repository.requestDetail(requestId);

      state = state.copyWith(isLoading: false, request: request);
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: _errorMessage(e));
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت جزئیات درخواست مشاوره ناموفق بود.',
      );
    }
  }

  Future<void> cancelRequest(int requestId, {String? note}) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final request = await _repository.cancelRequest(
        requestId: requestId,
        note: note,
      );

      state = state.copyWith(
        isSaving: false,
        request: request,
        successMessage: 'درخواست مشاوره لغو شد.',
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: _errorMessage(e));
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'لغو درخواست مشاوره ناموفق بود.',
      );
    }
  }

  Future<void> updateAssignedStatus({
    required int requestId,
    required String status,
  }) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final request = await _repository.updateAssignedRequestStatus(
        requestId: requestId,
        status: status,
      );

      state = state.copyWith(
        isSaving: false,
        request: request,
        successMessage: 'وضعیت درخواست به‌روزرسانی شد.',
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: _errorMessage(e));
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'به‌روزرسانی وضعیت درخواست ناموفق بود.',
      );
    }
  }

  String _errorMessage(ConsultantApiException exception) {
    if (exception.error.code == 'PERMISSION_DENIED') {
      return 'برای مشاهده این بخش دسترسی لازم را ندارید.';
    }

    if (exception.error.code == 'VALIDATION_ERROR') {
      return 'این عملیات با وضعیت فعلی درخواست سازگار نیست. صفحه را تازه‌سازی و دوباره تلاش کنید.';
    }

    return exception.error.message;
  }
}
