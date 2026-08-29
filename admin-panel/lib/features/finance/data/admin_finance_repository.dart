import 'admin_finance_api.dart';
import 'admin_finance_models.dart';

class AdminFinanceRepository {
  AdminFinanceRepository({AdminFinanceApi? api})
    : _api = api ?? AdminFinanceApi();
  final AdminFinanceApi _api;
  Future<AdminFinancePageResult> list(
    AdminFinanceResource resource, {
    required int page,
  }) => _api.list(resource, page: page);
  Future<AdminReconciliation> reconciliation() => _api.reconciliation();
  Future<void> decideSettlement(int id, String decision) =>
      _api.decideSettlement(id, decision);
  Future<void> simulatePayout(int id) => _api.simulatePayout(id);
  Future<void> decideBillingRefund(int id, String decision) =>
      _api.decideBillingRefund(id, decision);
  Future<void> completeMockBillingRefund(int id) =>
      _api.completeMockBillingRefund(id);
}
