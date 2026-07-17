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
}
