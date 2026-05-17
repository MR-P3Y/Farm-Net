import '../data/admin_verification_models.dart';

class AdminVerificationState {
  const AdminVerificationState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.selected,
    this.statusFilter,
    this.targetRoleFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminVerificationRequest> items;
  final AdminVerificationRequest? selected;
  final String? statusFilter;
  final String? targetRoleFilter;
  final String? errorMessage;

  factory AdminVerificationState.initial() {
    return const AdminVerificationState(isLoading: true);
  }

  AdminVerificationState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminVerificationRequest>? items,
    AdminVerificationRequest? selected,
    String? statusFilter,
    String? targetRoleFilter,
    String? errorMessage,
    bool clearSelected = false,
    bool clearStatusFilter = false,
    bool clearTargetRoleFilter = false,
    bool clearError = false,
  }) {
    return AdminVerificationState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      selected: clearSelected ? null : selected ?? this.selected,
      statusFilter:
          clearStatusFilter ? null : statusFilter ?? this.statusFilter,
      targetRoleFilter:
          clearTargetRoleFilter
              ? null
              : targetRoleFilter ?? this.targetRoleFilter,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
