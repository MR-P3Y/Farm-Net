import '../data/consultant_models.dart';

const Object _unset = Object();

class ConsultantListState {
  const ConsultantListState({
    required this.isLoading,
    this.isSaving = false,
    this.specialties = const [],
    this.consultants = const [],
    this.selectedSpecialtyId,
    this.query = '',
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<ConsultantSpecialtyModel> specialties;
  final List<ConsultantProfileModel> consultants;
  final int? selectedSpecialtyId;
  final String query;
  final String? errorMessage;

  factory ConsultantListState.initial() {
    return const ConsultantListState(isLoading: true);
  }

  ConsultantListState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ConsultantSpecialtyModel>? specialties,
    List<ConsultantProfileModel>? consultants,
    Object? selectedSpecialtyId = _unset,
    String? query,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ConsultantListState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      specialties: specialties ?? this.specialties,
      consultants: consultants ?? this.consultants,
      selectedSpecialtyId:
          identical(selectedSpecialtyId, _unset)
              ? this.selectedSpecialtyId
              : selectedSpecialtyId as int?,
      query: query ?? this.query,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
