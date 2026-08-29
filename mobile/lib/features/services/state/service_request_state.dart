import '../data/service_models.dart';

class ServiceRequestState {
  const ServiceRequestState({
    this.isLoading = false,
    this.isSaving = false,
    this.requests = const [],
    this.selected,
    this.finalPrice,
    this.paymentAttempt,
    this.errorMessage,
    this.successMessage,
  });
  final bool isLoading;
  final bool isSaving;
  final List<ServiceRequest> requests;
  final ServiceRequest? selected;
  final ServiceFinalPrice? finalPrice;
  final BillingPaymentAttempt? paymentAttempt;
  final String? errorMessage;
  final String? successMessage;
  ServiceRequestState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ServiceRequest>? requests,
    ServiceRequest? selected,
    ServiceFinalPrice? finalPrice,
    BillingPaymentAttempt? paymentAttempt,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
    bool clearFinalPrice = false,
    bool clearPaymentAttempt = false,
  }) => ServiceRequestState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    requests: requests ?? this.requests,
    selected: selected ?? this.selected,
    finalPrice: clearFinalPrice ? null : finalPrice ?? this.finalPrice,
    paymentAttempt:
        clearPaymentAttempt ? null : paymentAttempt ?? this.paymentAttempt,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}
