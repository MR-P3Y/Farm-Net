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
}
