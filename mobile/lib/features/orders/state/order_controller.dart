import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/order_api.dart';
import '../data/order_models.dart';
import '../data/order_repository.dart';
import 'order_state.dart';

final orderControllerProvider =
    StateNotifierProvider<OrderController, OrderState>((ref) {
      return OrderController(repository: ref.watch(orderRepositoryProvider));
    });

class OrderController extends StateNotifier<OrderState> {
  OrderController({required OrderRepository repository})
    : _repository = repository,
      super(OrderState.initial());

  final OrderRepository _repository;

  Future<void> loadCart() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final cart = await _repository.getMyCart();
      state = state.copyWith(isLoading: false, cart: cart);
    } on OrderApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت سبد خرید',
      );
    }
  }

  Future<bool> addToCart({required int productId, int quantity = 1}) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final cart = await _repository.addCartItem(
        productId: productId,
        quantity: quantity,
      );

      state = state.copyWith(isSaving: false, cart: cart);
      return true;
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در افزودن به سبد خرید',
      );
      return false;
    }
  }

  Future<void> updateCartItem({
    required int itemId,
    required int quantity,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final cart = await _repository.updateCartItem(
        itemId: itemId,
        quantity: quantity,
      );

      state = state.copyWith(isSaving: false, cart: cart);
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر تعداد',
      );
    }
  }

  Future<void> deleteCartItem(int itemId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final cart = await _repository.deleteCartItem(itemId);
      state = state.copyWith(isSaving: false, cart: cart);
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در حذف آیتم');
    }
  }

  Future<void> clearCart() async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final cart = await _repository.clearCart();
      state = state.copyWith(isSaving: false, cart: cart);
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در پاک کردن سبد',
      );
    }
  }

  Future<bool> checkout(CheckoutInput input) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearCheckout: true,
    );

    try {
      final result = await _repository.checkout(input);
      final cart = await _repository.getMyCart();

      state = state.copyWith(isSaving: false, cart: cart, lastCheckout: result);

      await loadMyOrders();
      return true;
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در ثبت سفارش');
      return false;
    }
  }

  Future<void> loadMyOrders({String? status}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final orders = await _repository.listMyOrders(status: status);
      state = state.copyWith(isLoading: false, orders: orders);
    } on OrderApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت سفارش‌ها',
      );
    }
  }

  Future<void> loadOrderDetail(int orderId) async {
    state = state.copyWith(
      isLoading: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final order = await _repository.getMyOrder(orderId);
      state = state.copyWith(isLoading: false, selectedOrder: order);
    } on OrderApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت جزئیات سفارش',
      );
    }
  }

  Future<bool> payOrder(Order order) async {
    final invoiceId = order.invoiceId;
    if (invoiceId == null) {
      state = state.copyWith(
        errorMessage: 'فاکتور پرداخت برای این سفارش موجود نیست',
      );
      return false;
    }
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final attempt = await _repository.initiatePayment(
        invoiceId: invoiceId,
        idempotencyKey: 'mobile-payment-invoice-$invoiceId',
      );
      await _repository.verifyPayment(attemptId: attempt.id);
      await loadOrderDetail(order.id);
      state = state.copyWith(isSaving: false);
      return true;
    } on OrderApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در شروع یا تأیید پرداخت',
      );
      return false;
    }
  }
}
