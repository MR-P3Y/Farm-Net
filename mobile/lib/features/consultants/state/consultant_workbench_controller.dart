import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_repository.dart';
import 'consultant_workbench_state.dart';

final consultantWorkbenchControllerProvider = StateNotifierProvider<
  ConsultantWorkbenchController,
  ConsultantWorkbenchState
>((ref) {
  return ConsultantWorkbenchController(
    repository: ref.watch(consultantRepositoryProvider),
  );
});

class ConsultantWorkbenchController
    extends StateNotifier<ConsultantWorkbenchState> {
  ConsultantWorkbenchController({required ConsultantRepository repository})
    : _repository = repository,
      super(ConsultantWorkbenchState.initial());

  final ConsultantRepository _repository;

  Future<void> load({String? status}) async {
    state = state.copyWith(
      isLoading: true,
      selectedStatus: status,
      clearStatus: status == null,
      clearError: true,
      clearSuccess: true,
    );

    try {
      final requests = await _repository.assignedRequests(status: status);
      state = state.copyWith(isLoading: false, requests: requests);
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: _errorMessage(e));
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت درخواست‌های ارجاع‌شده ناموفق بود.',
      );
    }
  }

  Future<void> updateStatus({
    required int requestId,
    required String status,
  }) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );

    try {
      await _repository.updateAssignedRequestStatus(
        requestId: requestId,
        status: status,
      );

      final requests = await _repository.assignedRequests(
        status: state.selectedStatus,
      );

      state = state.copyWith(
        isSaving: false,
        requests: requests,
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
      return 'برای استفاده از میزکار، پروفایل مشاور تأییدشده لازم است.';
    }

    return exception.error.message;
  }
}
