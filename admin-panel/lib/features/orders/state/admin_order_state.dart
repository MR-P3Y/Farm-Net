import '../data/admin_order_models.dart';

class AdminOrderState {
  const AdminOrderState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.selected,
    this.statusFilter,
    this.paymentStatusFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminOrder> items;
  final AdminOrder? selected;
  final String? statusFilter;
  final String? paymentStatusFilter;
  final String? errorMessage;

  factory AdminOrderState.initial() {
    return const AdminOrderState(isLoading: true);
  }

  AdminOrderState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminOrder>? items,
    AdminOrder? selected,
    String? statusFilter,
    String? paymentStatusFilter,
    String? errorMessage,
    bool clearSelected = false,
    bool clearError = false,
  }) {
    return AdminOrderState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      selected: clearSelected ? null : selected ?? this.selected,
      statusFilter: statusFilter ?? this.statusFilter,
      paymentStatusFilter: paymentStatusFilter ?? this.paymentStatusFilter,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
