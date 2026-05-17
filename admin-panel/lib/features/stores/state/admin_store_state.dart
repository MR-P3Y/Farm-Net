import '../data/admin_store_models.dart';

class AdminStoreState {
  const AdminStoreState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.selected,
    this.statusFilter,
    this.search,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminStore> items;
  final AdminStore? selected;
  final String? statusFilter;
  final String? search;
  final String? errorMessage;

  factory AdminStoreState.initial() {
    return const AdminStoreState(isLoading: true);
  }

  AdminStoreState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminStore>? items,
    AdminStore? selected,
    String? statusFilter,
    String? search,
    String? errorMessage,
    bool clearSelected = false,
    bool clearStatusFilter = false,
    bool clearSearch = false,
    bool clearError = false,
  }) {
    return AdminStoreState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      selected: clearSelected ? null : selected ?? this.selected,
      statusFilter:
          clearStatusFilter ? null : statusFilter ?? this.statusFilter,
      search: clearSearch ? null : search ?? this.search,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
