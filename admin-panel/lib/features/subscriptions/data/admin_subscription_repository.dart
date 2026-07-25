import 'admin_subscription_api.dart';
import 'admin_subscription_models.dart';

class AdminSubscriptionRepository {
  AdminSubscriptionRepository({AdminSubscriptionApi? api})
    : _api = api ?? AdminSubscriptionApi();

  final AdminSubscriptionApi _api;

  Future<AdminBillingPage<AdminBillingPlan>> plans({
    String? query,
    String? status,
    int page = 1,
  }) => _api.plans(query: query, status: status, page: page);

  Future<AdminBillingPlan> createPlan(Map<String, dynamic> payload) =>
      _api.createPlan(payload);

  Future<AdminBillingPlan> setPlanStatus(
    AdminBillingPlan plan,
    String status,
  ) => _api.setPlanStatus(plan, status);

  Future<AdminBillingPage<AdminBillingSubscription>> subscriptions({
    String? query,
    String? status,
    int page = 1,
  }) => _api.subscriptions(query: query, status: status, page: page);

  Future<AdminBillingSubscription> subscription(int id) =>
      _api.subscription(id);

  Future<AdminBillingSubscription> manualActivate({
    required int userId,
    required int planId,
    required String reason,
  }) => _api.manualActivate(userId: userId, planId: planId, reason: reason);

  Future<AdminBillingSubscription> cancel({
    required AdminBillingSubscription subscription,
    required String reason,
    required bool atPeriodEnd,
  }) => _api.cancel(
    subscription: subscription,
    reason: reason,
    atPeriodEnd: atPeriodEnd,
  );

  Future<AdminBillingPage<AdminBillingAudit>> audit({
    String? action,
    String? targetType,
    int page = 1,
  }) => _api.audit(action: action, targetType: targetType, page: page);

  Future<AdminBillingReconciliation> reconciliation() => _api.reconciliation();
}
