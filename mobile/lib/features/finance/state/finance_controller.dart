import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/finance_api.dart';
import '../data/finance_models.dart';
import '../data/finance_repository.dart';

class FinanceState {
  const FinanceState({
    this.loading = false,
    this.saving = false,
    this.wallet,
    this.invoices = const [],
    this.settlements = const [],
    this.error,
  });
  final bool loading;
  final bool saving;
  final WalletBalance? wallet;
  final List<FinanceInvoice> invoices;
  final List<Settlement> settlements;
  final String? error;
  FinanceState copyWith({
    bool? loading,
    bool? saving,
    WalletBalance? wallet,
    List<FinanceInvoice>? invoices,
    List<Settlement>? settlements,
    String? error,
    bool clearError = false,
  }) => FinanceState(
    loading: loading ?? this.loading,
    saving: saving ?? this.saving,
    wallet: wallet ?? this.wallet,
    invoices: invoices ?? this.invoices,
    settlements: settlements ?? this.settlements,
    error: clearError ? null : error ?? this.error,
  );
}

final financeControllerProvider =
    StateNotifierProvider<FinanceController, FinanceState>(
      (ref) => FinanceController(ref.watch(financeRepositoryProvider)),
    );

class FinanceController extends StateNotifier<FinanceState> {
  FinanceController(this._repository) : super(const FinanceState());
  final FinanceRepository _repository;
  Future<void> load() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final invoices = await _repository.invoices();
      WalletBalance? wallet;
      List<Settlement> settlements = const [];
      try {
        wallet = await _repository.wallet();
        settlements = await _repository.settlements();
      } on FinanceApiException {
        // Buyer-only roles can still read their invoices without provider wallet permissions.
      }
      state = FinanceState(
        wallet: wallet,
        invoices: invoices,
        settlements: settlements,
      );
    } on FinanceApiException catch (error) {
      state = state.copyWith(loading: false, error: error.error.message);
    } catch (_) {
      state = state.copyWith(
        loading: false,
        error: 'دریافت اطلاعات مالی ناموفق بود.',
      );
    }
  }

  Future<bool> requestSettlement(double amount, String? note) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      await _repository.createSettlement(amount, note);
      await load();
      return true;
    } on FinanceApiException catch (error) {
      state = state.copyWith(saving: false, error: error.error.message);
      return false;
    }
  }
}
