import 'package:farm_net_admin/features/subscriptions/data/admin_subscription_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('admin plan parses typed TOMAN feature contract', () {
    final plan = AdminBillingPlan.fromJson({
      'id': 2,
      'code': 'farmer_plus',
      'name': 'کشاورز پلاس',
      'description': null,
      'status': 'draft',
      'billing_period': 'monthly',
      'duration_days': null,
      'price_toman': '250000.00',
      'currency': 'TOMAN',
      'version': 2,
      'is_default_free': false,
      'effective_from': null,
      'effective_until': null,
      'features': [
        {
          'code': 'ai.text_chat',
          'name': 'AI chat',
          'module': 'ai',
          'value_kind': 'integer',
          'unit': 'request',
          'enabled': true,
          'unlimited': false,
          'value': '100.0000',
        },
      ],
    });

    expect(plan.priceToman, 250000);
    expect(plan.currency, 'TOMAN');
    expect(plan.features.single.code, 'ai.text_chat');
    expect(plan.features.single.toInput()['numeric_value'], '100.0000');
  });

  test('admin subscription parses provenance and reserved usage', () {
    final subscription = AdminBillingSubscription.fromJson({
      'id': 8,
      'user_id': 4,
      'user_label': '09120000000',
      'status': 'active',
      'plan_id': 2,
      'plan_code': 'professional',
      'plan_name': 'حرفه‌ای',
      'price_toman': '900000',
      'currency': 'TOMAN',
      'starts_at': '2026-07-26T10:00:00',
      'current_period_starts_at': '2026-07-26T10:00:00',
      'current_period_ends_at': '2026-08-25T10:00:00',
      'grace_ends_at': null,
      'auto_renew': false,
      'cancel_at_period_end': false,
      'activation_source': 'admin',
      'activated_by_user_id': 1,
      'activation_reason': 'Support grant',
      'cancellation_reason': null,
      'version': 1,
      'usage': [
        {
          'code': 'ai.text_chat',
          'used_value': '2',
          'reserved_value': '1',
          'limit_value': '100',
          'remaining_value': '97',
          'unlimited': false,
        },
      ],
    });

    expect(subscription.activationSource, 'admin');
    expect(subscription.usage.single.reserved, 1);
    expect(subscription.usage.single.remaining, 97);
  });
}
