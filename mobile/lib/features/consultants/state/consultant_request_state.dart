import '../data/consultant_models.dart';

class ConsultantRequestState {
  const ConsultantRequestState({
    required this.isLoading,
    this.isSaving = false,
    this.requests = const [],
    this.errorMessage,
    this.successMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<ConsultationRequestModel> requests;
  final String? errorMessage;
  final String? successMessage;

  factory ConsultantRequestState.initial() {
    return const ConsultantRequestState(isLoading: false);
  }

  ConsultantRequestState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ConsultationRequestModel>? requests,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) {
    return ConsultantRequestState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      requests: requests ?? this.requests,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      successMessage:
          clearSuccess ? null : successMessage ?? this.successMessage,
    );
  }
}
