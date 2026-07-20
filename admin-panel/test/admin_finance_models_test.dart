import 'package:farm_net_admin/features/finance/data/admin_finance_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('invoice response stays typed', () {
    final row = AdminFinanceRecord.fromJson(AdminFinanceResource.invoices, {
      'id': 7,
      'invoice_number': 'INV-7',
      'status': 'paid',
      'total_amount': 125000,
      'created_at': '2026-07-17T10:00:00',
    });
    expect(row.id, 7);
    expect(row.title, 'INV-7');
    expect(row.amount, 125000);
  });

  test('audit response exposes typed traceability fields', () {
    final row = AdminFinanceRecord.fromJson(AdminFinanceResource.auditLogs, {
      'id': 9,
      'action': 'FINANCE_REFUND_COMPLETED',
      'target_type': 'finance_refund',
      'trace_id': 'trace-9',
      'created_at': '2026-07-17T11:00:00',
    });
    expect(row.status, 'finance_refund');
    expect(row.reference, 'trace-9');
  });

  test('ledger and settlement responses stay typed', () {
    final journal = AdminFinanceRecord.fromJson(AdminFinanceResource.ledger, {
      'id': 10,
      'journal_number': 'JRN-10',
      'status': 'posted',
      'total_debit': 5000,
      'trace_id': 'trace-10',
      'posted_at': '2026-07-20T10:00:00',
    });
    final settlement =
        AdminFinanceRecord.fromJson(AdminFinanceResource.settlements, {
          'id': 11,
          'status': 'requested',
          'amount': 4000,
          'requested_at': '2026-07-20T11:00:00',
        });
    expect(journal.title, 'JRN-10');
    expect(journal.amount, 5000);
    expect(settlement.status, 'requested');
    expect(settlement.createdAt, isNotNull);
  });

  test('reconciliation summarizes mismatch arrays without raw json', () {
    final row = AdminReconciliation.fromJson({
      'is_clean': false,
      'missing_payment_transaction_ids': [1, 2],
      'missing_refund_transaction_ids': [3],
      'unbalanced_journal_ids': [],
    });
    expect(row.clean, isFalse);
    expect(row.missingPayments, 2);
    expect(row.missingRefunds, 1);
  });
}
