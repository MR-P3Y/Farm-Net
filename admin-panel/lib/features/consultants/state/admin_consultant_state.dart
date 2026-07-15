import '../data/admin_consultant_models.dart';

const _unset = Object();

class AdminConsultantState {
  const AdminConsultantState({
    required this.isLoading,
    this.isSaving = false,
    this.specialties = const [],
    this.profiles = const [],
    this.requests = const [],
    this.selectedRequest,
    this.profileStatusFilter,
    this.requestStatusFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminConsultSpecialty> specialties;
  final List<AdminConsultProfile> profiles;
  final List<AdminConsultRequest> requests;
  final AdminConsultRequest? selectedRequest;
  final String? profileStatusFilter;
  final String? requestStatusFilter;
  final String? errorMessage;

  factory AdminConsultantState.initial() {
    return const AdminConsultantState(isLoading: true);
  }

  AdminConsultantState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminConsultSpecialty>? specialties,
    List<AdminConsultProfile>? profiles,
    List<AdminConsultRequest>? requests,
    AdminConsultRequest? selectedRequest,
    Object? profileStatusFilter = _unset,
    Object? requestStatusFilter = _unset,
    String? errorMessage,
    bool clearSelectedRequest = false,
    bool clearError = false,
  }) {
    return AdminConsultantState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      specialties: specialties ?? this.specialties,
      profiles: profiles ?? this.profiles,
      requests: requests ?? this.requests,
      selectedRequest:
          clearSelectedRequest ? null : selectedRequest ?? this.selectedRequest,
      profileStatusFilter:
          identical(profileStatusFilter, _unset)
              ? this.profileStatusFilter
              : profileStatusFilter as String?,
      requestStatusFilter:
          identical(requestStatusFilter, _unset)
              ? this.requestStatusFilter
              : requestStatusFilter as String?,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
