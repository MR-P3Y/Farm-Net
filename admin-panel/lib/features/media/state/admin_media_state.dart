import '../data/admin_media_models.dart';

class AdminMediaState {
  const AdminMediaState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.selected,
    this.purposeFilter,
    this.visibilityFilter,
    this.statusFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminMediaFile> items;
  final AdminMediaFile? selected;
  final String? purposeFilter;
  final String? visibilityFilter;
  final String? statusFilter;
  final String? errorMessage;

  factory AdminMediaState.initial() {
    return const AdminMediaState(isLoading: true);
  }

  AdminMediaState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminMediaFile>? items,
    AdminMediaFile? selected,
    String? purposeFilter,
    String? visibilityFilter,
    String? statusFilter,
    String? errorMessage,
    bool clearSelected = false,
    bool clearError = false,
  }) {
    return AdminMediaState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      selected: clearSelected ? null : selected ?? this.selected,
      purposeFilter: purposeFilter ?? this.purposeFilter,
      visibilityFilter: visibilityFilter ?? this.visibilityFilter,
      statusFilter: statusFilter ?? this.statusFilter,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
