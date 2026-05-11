import '../../documents/data/document_models.dart';
import '../data/verification_models.dart';

class VerificationState {
  const VerificationState({
    required this.isLoading,
    this.isSaving = false,
    this.requests = const [],
    this.documents = const [],
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<VerificationRequest> requests;
  final List<UserDocument> documents;
  final String? errorMessage;

  factory VerificationState.initial() {
    return const VerificationState(isLoading: true);
  }

  VerificationState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<VerificationRequest>? requests,
    List<UserDocument>? documents,
    String? errorMessage,
    bool clearError = false,
  }) {
    return VerificationState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      requests: requests ?? this.requests,
      documents: documents ?? this.documents,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
