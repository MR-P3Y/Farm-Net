import '../data/consultant_models.dart';

class ConsultantRequestDetailState {
  const ConsultantRequestDetailState({
    required this.isLoading,
    this.isSaving = false,
    this.request,
    this.errorMessage,
    this.successMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final ConsultationRequestModel? request;
  final String? errorMessage;
  final String? successMessage;

  factory ConsultantRequestDetailState.initial() {
    return const ConsultantRequestDetailState(isLoading: true);
  }

  ConsultantRequestDetailState copyWith({
    bool? isLoading,
    bool? isSaving,
    ConsultationRequestModel? request,
    String? errorMessage,
    String? successMessage,
    bool clearRequest = false,
    bool clearError = false,
    bool clearSuccess = false,
  }) {
    return ConsultantRequestDetailState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      request: clearRequest ? null : request ?? this.request,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      successMessage:
          clearSuccess ? null : successMessage ?? this.successMessage,
    );
  }
}
