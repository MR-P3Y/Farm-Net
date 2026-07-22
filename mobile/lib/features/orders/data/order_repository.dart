import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'order_api.dart';
import 'order_models.dart';

final orderRepositoryProvider = Provider<OrderRepository>((ref) {
  return OrderRepository(api: OrderApi());
});

class OrderRepository {
  OrderRepository({required OrderApi api}) : _api = api;

  final OrderApi _api;

  Future<Cart> getMyCart() {
    return _api.getMyCart();
  }

  Future<Cart> addCartItem({required int productId, required int quantity}) {
    return _api.addCartItem(productId: productId, quantity: quantity);
  }

  Future<Cart> updateCartItem({required int itemId, required int quantity}) {
    return _api.updateCartItem(itemId: itemId, quantity: quantity);
  }

  Future<Cart> deleteCartItem(int itemId) {
    return _api.deleteCartItem(itemId);
  }

  Future<Cart> clearCart() {
    return _api.clearCart();
  }

  Future<CheckoutResult> checkout(CheckoutInput input) {
    return _api.checkout(input);
  }

  Future<List<Order>> listMyOrders({String? status}) {
    return _api.listMyOrders(status: status);
  }

  Future<Order> getMyOrder(int orderId) {
    return _api.getMyOrder(orderId);
  }

  Future<SellerOrderPage> listSellerOrders({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) => _api.listSellerOrders(page: page, pageSize: pageSize, status: status);

  Future<Order> getSellerOrder(int orderId) => _api.getSellerOrder(orderId);

  Future<Order> updateSellerOrderStatus({
    required int orderId,
    required String status,
    String? sellerNote,
  }) => _api.updateSellerOrderStatus(
    orderId: orderId,
    status: status,
    sellerNote: sellerNote,
  );

  Future<List<Payment>> listMyPayments({String? status}) {
    return _api.listMyPayments(status: status);
  }

  Future<PaymentAttempt> initiatePayment({
    required int invoiceId,
    required String idempotencyKey,
  }) => _api.initiatePayment(
    invoiceId: invoiceId,
    idempotencyKey: idempotencyKey,
  );

  Future<PaymentAttempt> verifyPayment({required int attemptId}) =>
      _api.verifyPayment(attemptId: attemptId);
}
