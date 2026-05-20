import '../data/admin_product_models.dart';

class AdminProductState {
  const AdminProductState({
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
  final List<AdminProduct> items;
  final AdminProduct? selected;
  final String? statusFilter;
  final String? search;
  final String? errorMessage;

  factory AdminProductState.initial() {
    return const AdminProductState(isLoading: true);
  }

  AdminProductState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminProduct>? items,
    AdminProduct? selected,
    String? statusFilter,
    String? search,
    String? errorMessage,
    bool clearSelected = false,
    bool clearStatusFilter = false,
    bool clearSearch = false,
    bool clearError = false,
  }) {
    return AdminProductState(
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
