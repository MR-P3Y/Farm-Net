import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'finance_api.dart';
import 'finance_models.dart';

final financeRepositoryProvider = Provider<FinanceRepository>(
  (ref) => FinanceRepository(FinanceApi()),
);

class FinanceRepository {
  FinanceRepository(this._api);
  final FinanceApi _api;
  Future<WalletBalance> wallet() => _api.wallet();
  Future<List<FinanceInvoice>> invoices() => _api.invoices();
  Future<List<Settlement>> settlements() => _api.settlements();
  Future<Settlement> createSettlement(double amount, String? note) =>
      _api.createSettlement(amount, note);
}
