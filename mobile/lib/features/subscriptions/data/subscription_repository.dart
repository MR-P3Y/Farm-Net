import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'subscription_api.dart';
import 'subscription_models.dart';

final subscriptionRepositoryProvider = Provider<SubscriptionRepository>(
  (ref) => SubscriptionRepository(SubscriptionApi()),
);

class SubscriptionRepository {
  SubscriptionRepository(this._api);
  final SubscriptionApi _api;

  Future<List<SubscriptionPlan>> plans() => _api.plans();
  Future<OwnSubscription?> current() => _api.current();
  Future<List<SubscriptionEntitlement>> entitlements() => _api.entitlements();
  Future<List<SubscriptionUsage>> usage() => _api.usage();
  Future<OwnSubscription> activateFree() => _api.activateFree();
  Future<SubscriptionCheckout> checkout(
    String planCode,
    String provider,
    String key,
  ) => _api.checkout(
    planCode: planCode,
    provider: provider,
    idempotencyKey: key,
  );
  Future<SubscriptionCheckout> renewalCheckout(String provider, String key) =>
      _api.renewalCheckout(provider: provider, idempotencyKey: key);
  Future<SubscriptionCheckout> verify(int attemptId, String token) =>
      _api.verify(paymentAttemptId: attemptId, providerToken: token);
  Future<OwnSubscription> cancel(int version, String reason) =>
      _api.cancel(expectedVersion: version, reason: reason);
  Future<OwnSubscription> resume(int version) =>
      _api.resume(expectedVersion: version);
}
