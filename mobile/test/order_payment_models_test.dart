import 'package:farm_net/features/orders/data/order_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('payment attempt parses typed contract', () {
    final attempt = PaymentAttempt.fromJson({
      'id': 12,
      'invoice_id': 8,
      'order_id': 4,
      'provider': 'mock',
      'status': 'redirected',
      'redirect_url': 'farmnet://payments/mock/12',
    });
    expect(attempt.invoiceId, 8);
    expect(attempt.status, 'redirected');
  });

  test('checkout input preserves replay key', () {
    const input = CheckoutInput(idempotencyKey: 'mobile-checkout-1');
    expect(input.toJson()['idempotency_key'], 'mobile-checkout-1');
  });

  test('seller order page parses privacy-limited list and pagination', () {
    final page = SellerOrderPage.fromEnvelope({
      'data': [
        {
          'id': 9,
          'order_number': 'FN-9',
          'buyer_user_id': 12,
          'store_id': 3,
          'status': 'paid',
          'payment_status': 'paid',
          'currency': 'TOMAN',
          'subtotal_amount': '120000',
          'discount_amount': '0',
          'shipping_amount': '0',
          'total_amount': '120000',
          'seller_amount': '110000',
          'created_at': '2026-07-22T10:00:00',
          'updated_at': '2026-07-22T10:00:00',
          'items': [],
        },
      ],
      'meta': {'page': 2, 'page_size': 20, 'total': 25, 'total_pages': 2},
    });

    expect(page.page, 2);
    expect(page.total, 25);
    expect(page.items.single.sellerAmount, 110000);
    expect(page.items.single.shippingAddress, isNull);
    expect(page.items.single.commissionAmount, 0);
  });

  test('seller next status follows backend transition matrix exactly', () {
    Order order(String status, {String paymentStatus = 'paid'}) =>
        Order.fromJson({
          'id': 1,
          'order_number': 'FN-1',
          'buyer_user_id': 2,
          'store_id': 3,
          'status': status,
          'payment_status': paymentStatus,
          'currency': 'TOMAN',
          'subtotal_amount': 1,
          'discount_amount': 0,
          'shipping_amount': 0,
          'total_amount': 1,
          'seller_amount': 1,
          'created_at': '',
          'updated_at': '',
        });

    expect(order('paid').sellerNextStatus, 'confirmed');
    expect(order('confirmed').sellerNextStatus, 'processing');
    expect(order('processing').sellerNextStatus, 'shipped');
    expect(order('shipped').sellerNextStatus, 'delivered');
    expect(order('delivered').sellerNextStatus, isNull);
    expect(order('paid', paymentStatus: 'pending').sellerNextStatus, isNull);
  });
}
