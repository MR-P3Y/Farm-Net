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
}
