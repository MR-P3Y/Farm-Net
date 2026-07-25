import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/subscription_api.dart';
import '../data/subscription_models.dart';
import '../data/subscription_repository.dart';

class SubscriptionState {
  const SubscriptionState({
    this.loading = false,
    this.saving = false,
    this.plans = const [],
    this.current,
    this.entitlements = const [],
    this.usage = const [],
    this.error,
  });

  final bool loading;
  final bool saving;
  final List<SubscriptionPlan> plans;
  final OwnSubscription? current;
  final List<SubscriptionEntitlement> entitlements;
  final List<SubscriptionUsage> usage;
  final String? error;

  SubscriptionState copyWith({
    bool? loading,
    bool? saving,
    List<SubscriptionPlan>? plans,
    OwnSubscription? current,
    bool clearCurrent = false,
    List<SubscriptionEntitlement>? entitlements,
    List<SubscriptionUsage>? usage,
    String? error,
    bool clearError = false,
  }) => SubscriptionState(
    loading: loading ?? this.loading,
    saving: saving ?? this.saving,
    plans: plans ?? this.plans,
    current: clearCurrent ? null : current ?? this.current,
    entitlements: entitlements ?? this.entitlements,
    usage: usage ?? this.usage,
    error: clearError ? null : error ?? this.error,
  );
}

final subscriptionControllerProvider = StateNotifierProvider<
  SubscriptionController,
  SubscriptionState
>((ref) => SubscriptionController(ref.watch(subscriptionRepositoryProvider)));

class SubscriptionController extends StateNotifier<SubscriptionState> {
  SubscriptionController(this._repository) : super(const SubscriptionState());
  final SubscriptionRepository _repository;

  Future<void> load() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final plans = await _repository.plans();
      final current = await _repository.current();
      var entitlements = <SubscriptionEntitlement>[];
      var usage = <SubscriptionUsage>[];
      if (current != null) {
        entitlements = await _repository.entitlements();
        usage = await _repository.usage();
      }
      state = SubscriptionState(
        plans: plans,
        current: current,
        entitlements: entitlements,
        usage: usage,
      );
    } on SubscriptionApiException catch (error) {
      state = state.copyWith(loading: false, error: error.error.message);
    } catch (_) {
      state = state.copyWith(
        loading: false,
        error: 'دریافت اطلاعات اشتراک ناموفق بود.',
      );
    }
  }

  Future<bool> activateFree() => _mutate(() => _repository.activateFree());

  Future<SubscriptionCheckout?> checkout(
    SubscriptionPlan plan,
    String provider,
  ) => _payment(() {
    final key = 'mobile-sub-${DateTime.now().microsecondsSinceEpoch}';
    return _repository.checkout(plan.code, provider, key);
  });

  Future<SubscriptionCheckout?> renewalCheckout(String provider) =>
      _payment(() {
        final key = 'mobile-renew-${DateTime.now().microsecondsSinceEpoch}';
        return _repository.renewalCheckout(provider, key);
      });

  Future<bool> verify(SubscriptionCheckout checkout, String token) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      await _repository.verify(checkout.paymentAttemptId, token);
      await load();
      return true;
    } on SubscriptionApiException catch (error) {
      state = state.copyWith(saving: false, error: error.error.message);
      return false;
    }
  }

  Future<bool> cancel(String reason) {
    final current = state.current;
    if (current == null) return Future.value(false);
    return _mutate(() => _repository.cancel(current.version, reason));
  }

  Future<bool> resume() {
    final current = state.current;
    if (current == null) return Future.value(false);
    return _mutate(() => _repository.resume(current.version));
  }

  Future<bool> _mutate(Future<OwnSubscription> Function() action) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      await action();
      await load();
      return true;
    } on SubscriptionApiException catch (error) {
      state = state.copyWith(saving: false, error: error.error.message);
      return false;
    }
  }

  Future<SubscriptionCheckout?> _payment(
    Future<SubscriptionCheckout> Function() action,
  ) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      final checkout = await action();
      state = state.copyWith(saving: false);
      return checkout;
    } on SubscriptionApiException catch (error) {
      state = state.copyWith(saving: false, error: error.error.message);
      return null;
    }
  }
}
