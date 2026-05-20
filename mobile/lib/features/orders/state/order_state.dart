import '../data/order_models.dart';

class OrderState {
  const OrderState({
    required this.isLoading,
    this.isSaving = false,
    this.cart,
    this.orders = const [],
    this.selectedOrder,
    this.lastCheckout,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;

  final Cart? cart;
  final List<Order> orders;
  final Order? selectedOrder;
  final CheckoutResult? lastCheckout;
  final String? errorMessage;

  factory OrderState.initial() {
    return const OrderState(isLoading: false);
  }

  OrderState copyWith({
    bool? isLoading,
    bool? isSaving,
    Cart? cart,
    List<Order>? orders,
    Order? selectedOrder,
    CheckoutResult? lastCheckout,
    String? errorMessage,
    bool clearSelected = false,
    bool clearCheckout = false,
    bool clearError = false,
  }) {
    return OrderState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      cart: cart ?? this.cart,
      orders: orders ?? this.orders,
      selectedOrder: clearSelected ? null : selectedOrder ?? this.selectedOrder,
      lastCheckout: clearCheckout ? null : lastCheckout ?? this.lastCheckout,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
