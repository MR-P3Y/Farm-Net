import '../data/consultant_models.dart';

class ConsultantProfileState {
  const ConsultantProfileState({
    required this.isLoading,
    this.isSaving = false,
    this.profile,
    this.specialties = const [],
    this.errorMessage,
    this.successMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final ConsultantProfileModel? profile;
  final List<ConsultantSpecialtyModel> specialties;
  final String? errorMessage;
  final String? successMessage;

  factory ConsultantProfileState.initial() {
    return const ConsultantProfileState(isLoading: true);
  }

  ConsultantProfileState copyWith({
    bool? isLoading,
    bool? isSaving,
    ConsultantProfileModel? profile,
    List<ConsultantSpecialtyModel>? specialties,
    String? errorMessage,
    String? successMessage,
    bool clearProfile = false,
    bool clearError = false,
    bool clearSuccess = false,
  }) {
    return ConsultantProfileState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      profile: clearProfile ? null : profile ?? this.profile,
      specialties: specialties ?? this.specialties,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      successMessage:
          clearSuccess ? null : successMessage ?? this.successMessage,
    );
  }
}
