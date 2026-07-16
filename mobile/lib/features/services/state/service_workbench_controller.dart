import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/service_api.dart';
import '../data/service_models.dart';
import '../data/service_repository.dart';

class ServiceWorkbenchState {
  const ServiceWorkbenchState({
    this.isLoading = false,
    this.isSaving = false,
    this.requests = const [],
    this.selected,
    this.statusFilter,
    this.errorMessage,
    this.successMessage,
    this.isProviderUnapproved = false,
  });
  final bool isLoading, isSaving, isProviderUnapproved;
  final List<ServiceRequest> requests;
  final ServiceRequest? selected;
  final String? statusFilter, errorMessage, successMessage;
  ServiceWorkbenchState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ServiceRequest>? requests,
    ServiceRequest? selected,
    String? statusFilter,
    String? errorMessage,
    String? successMessage,
    bool? isProviderUnapproved,
    bool clearError = false,
    bool clearSuccess = false,
  }) => ServiceWorkbenchState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    requests: requests ?? this.requests,
    selected: selected ?? this.selected,
    statusFilter: statusFilter ?? this.statusFilter,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
    isProviderUnapproved: isProviderUnapproved ?? this.isProviderUnapproved,
  );
}

final serviceWorkbenchProvider =
    StateNotifierProvider<ServiceWorkbenchController, ServiceWorkbenchState>(
      (ref) => ServiceWorkbenchController(
        repository: ref.watch(serviceRepositoryProvider),
      ),
    );

class ServiceWorkbenchController extends StateNotifier<ServiceWorkbenchState> {
  ServiceWorkbenchController({required ServiceRepository repository})
    : _repository = repository,
      super(const ServiceWorkbenchState());
  final ServiceRepository _repository;
  Future<void> loadList({String? status}) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      clearError: true,
      clearSuccess: true,
      isProviderUnapproved: false,
    );
    try {
      final rows = await _repository.assignedRequests(status: status);
      state = state.copyWith(isLoading: false, requests: rows);
    } on ServiceApiException catch (e) {
      _error(e, isLoading: false);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت میزکار ناموفق بود.',
      );
    }
  }

  Future<void> loadDetail(int id) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
      isProviderUnapproved: false,
    );
    try {
      final row = await _repository.assignedRequestDetail(id);
      state = state.copyWith(isLoading: false, selected: row);
    } on ServiceApiException catch (e) {
      _error(e, isLoading: false);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت جزئیات درخواست ناموفق بود.',
      );
    }
  }

  Future<bool> update(int id, String status, {String? note}) async {
    if (state.isSaving) return false;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final row = await _repository.updateAssignedRequest(
        id,
        ServiceRequestStatusUpdateInput(status: status, note: note),
      );
      final list = await _repository.assignedRequests(
        status: state.statusFilter,
      );
      state = state.copyWith(
        isSaving: false,
        selected: row,
        requests: list,
        successMessage: 'وضعیت درخواست به‌روزرسانی شد.',
      );
      return true;
    } on ServiceApiException catch (e) {
      _error(e, isSaving: false);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'تغییر وضعیت ناموفق بود.',
      );
      return false;
    }
  }

  void _error(ServiceApiException e, {bool? isLoading, bool? isSaving}) {
    final denied = e.error.code == 'PERMISSION_DENIED';
    state = state.copyWith(
      isLoading: isLoading,
      isSaving: isSaving,
      isProviderUnapproved: denied,
      errorMessage:
          denied
              ? 'برای استفاده از میزکار، پروفایل خدمات‌دهنده شما باید تأیید شده باشد.'
              : e.error.message,
    );
  }
}
