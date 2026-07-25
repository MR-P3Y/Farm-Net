import 'package:farm_net/features/subscriptions/data/subscription_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('plan parses TOMAN price and typed feature values', () {
    final plan = SubscriptionPlan.fromJson({
      'id': 2,
      'code': 'farmer_plus',
      'name': 'کشاورز پلاس',
      'billing_period': 'monthly',
      'duration_days': null,
      'price_toman': '250000.00',
      'currency': 'TOMAN',
      'version': 3,
      'is_default_free': false,
      'features': [
        {
          'code': 'ai.text_chat',
          'name': 'گفت‌وگوی هوشمند',
          'module': 'ai',
          'unit': 'request',
          'enabled': true,
          'unlimited': false,
          'value': 100,
        },
      ],
    });

    expect(plan.priceToman, 250000);
    expect(plan.currency, 'TOMAN');
    expect(plan.isFree, isFalse);
    expect(plan.features.single.value, 100);
  });

  test('current subscription parses grace and nested plan', () {
    final subscription = OwnSubscription.fromJson({
      'id': 10,
      'status': 'grace',
      'plan': {
        'id': 2,
        'code': 'professional',
        'name': 'حرفه‌ای',
        'billing_period': 'yearly',
        'price_toman': 2000000,
        'currency': 'TOMAN',
        'version': 1,
        'is_default_free': false,
        'features': [],
      },
      'starts_at': '2026-01-01T00:00:00',
      'current_period_starts_at': '2026-01-01T00:00:00',
      'current_period_ends_at': '2027-01-01T00:00:00',
      'grace_ends_at': '2027-01-04T00:00:00',
      'auto_renew': true,
      'cancel_at_period_end': false,
      'version': 4,
    });

    expect(subscription.isInGrace, isTrue);
    expect(subscription.plan.code, 'professional');
    expect(subscription.graceEndsAt, isNotNull);
  });

  test('usage includes reserved value in visible consumption', () {
    final usage = SubscriptionUsage.fromJson({
      'code': 'ai.image_analysis',
      'used_value': '2.0000',
      'reserved_value': '1.0000',
      'limit_value': '10.0000',
      'remaining_value': '7.0000',
      'unlimited': false,
      'period_ends_at': '2026-08-26T00:00:00',
    });

    expect(usage.used + usage.reserved, 3);
    expect(usage.remaining, 7);
  });

  test('checkout model exposes redirect but no authority contract', () {
    final checkout = SubscriptionCheckout.fromJson({
      'payment_attempt_id': 12,
      'subscription_id': 5,
      'invoice_id': 8,
      'provider': 'zarinpal',
      'status': 'redirected',
      'amount_toman': '350000',
      'currency': 'TOMAN',
      'redirect_url': 'https://gateway.example/start',
      'expires_at': '2026-07-26T05:00:00',
      'verified_at': null,
      'provider_authority': 'must-not-be-modeled',
    });

    expect(checkout.amountToman, 350000);
    expect(checkout.redirectUrl, startsWith('https://'));
  });
}
