import 'package:farm_net/features/subscriptions/data/subscription_api.dart';
import 'package:farm_net/features/subscriptions/data/subscription_models.dart';
import 'package:farm_net/features/subscriptions/data/subscription_repository.dart';
import 'package:farm_net/features/subscriptions/presentation/subscription_center_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeSubscriptionRepository extends SubscriptionRepository {
  _FakeSubscriptionRepository() : super(SubscriptionApi());

  final free = SubscriptionPlan(
    id: 1,
    code: 'free',
    name: 'رایگان',
    description: 'دسترسی پایه فارم‌نت',
    billingPeriod: 'free',
    priceToman: 0,
    currency: 'TOMAN',
    version: 1,
    isDefaultFree: true,
    features: const [],
  );

  @override
  Future<List<SubscriptionPlan>> plans() async => [free];

  @override
  Future<OwnSubscription?> current() async => null;

  @override
  Future<List<SubscriptionEntitlement>> entitlements() async => [];

  @override
  Future<List<SubscriptionUsage>> usage() async => [];
}

void main() {
  testWidgets('subscription center renders empty state and free plan', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          subscriptionRepositoryProvider.overrideWithValue(
            _FakeSubscriptionRepository(),
          ),
        ],
        child: const MaterialApp(home: SubscriptionCenterScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('اشتراک فعالی ندارید'), findsOneWidget);
    expect(find.text('فعال‌سازی رایگان'), findsOneWidget);
    expect(find.textContaining('تومان ایران'), findsOneWidget);
  });
}
