import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net/features/finance/data/finance_models.dart';

void main() {
  test('wallet parses canonical TOMAN balances', () {
    final wallet = WalletBalance.fromJson({
      'currency': 'TOMAN',
      'pending_amount': 1200,
      'available_amount': 3400.0,
      'reserved_amount': 500,
    });
    expect(wallet.currency, 'TOMAN');
    expect(wallet.available, 3400);
    expect(wallet.pending, 1200);
    expect(wallet.reserved, 500);
  });

  test('own invoice excludes commission/provider fields by model contract', () {
    final invoice = FinanceInvoice.fromJson({
      'id': 1,
      'invoice_number': 'INV-1',
      'source_type': 'product_order',
      'source_id': 2,
      'status': 'paid',
      'currency': 'TOMAN',
      'total_amount': 10000,
      'issued_at': '2026-07-20T10:00:00',
      'platform_amount': 1000,
      'provider_amount': 9000,
    });
    expect(invoice.total, 10000);
    expect(invoice.sourceType, 'product_order');
  });

  test('settlement parses status and toman amount', () {
    final settlement = Settlement.fromJson({
      'id': 4,
      'requester_user_id': 7,
      'amount': 5000,
      'currency': 'TOMAN',
      'status': 'requested',
      'note': null,
      'admin_note': null,
      'requested_at': '2026-07-20T10:00:00',
      'decided_at': null,
      'simulated_completed_at': null,
    });
    expect(settlement.status, 'requested');
    expect(settlement.amount, 5000);
  });
}
