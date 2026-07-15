import '../data/consultant_models.dart';

class ConsultantWorkbenchState {
  const ConsultantWorkbenchState({
    required this.isLoading,
    this.isSaving = false,
    this.requests = const [],
    this.selectedStatus,
    this.errorMessage,
    this.successMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<ConsultationRequestModel> requests;
  final String? selectedStatus;
  final String? errorMessage;
  final String? successMessage;

  factory ConsultantWorkbenchState.initial() {
    return const ConsultantWorkbenchState(isLoading: false);
  }

  ConsultantWorkbenchState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ConsultationRequestModel>? requests,
    String? selectedStatus,
    String? errorMessage,
    String? successMessage,
    bool clearStatus = false,
    bool clearError = false,
    bool clearSuccess = false,
  }) {
    return ConsultantWorkbenchState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      requests: requests ?? this.requests,
      selectedStatus:
          clearStatus ? null : selectedStatus ?? this.selectedStatus,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      successMessage:
          clearSuccess ? null : successMessage ?? this.successMessage,
    );
  }
}
