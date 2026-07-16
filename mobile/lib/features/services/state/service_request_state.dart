import '../data/service_models.dart';

class ServiceRequestState {
  const ServiceRequestState({
    this.isLoading = false,
    this.isSaving = false,
    this.requests = const [],
    this.selected,
    this.errorMessage,
    this.successMessage,
  });
  final bool isLoading;
  final bool isSaving;
  final List<ServiceRequest> requests;
  final ServiceRequest? selected;
  final String? errorMessage;
  final String? successMessage;
  ServiceRequestState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ServiceRequest>? requests,
    ServiceRequest? selected,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) => ServiceRequestState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    requests: requests ?? this.requests,
    selected: selected ?? this.selected,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}
