enum AdminFinanceResource {
  invoices,
  paymentAttempts,
  transactions,
  refunds,
  auditLogs,
  ledger,
  wallets,
  settlements,
}

extension AdminFinanceResourceX on AdminFinanceResource {
  String get path => switch (this) {
    AdminFinanceResource.invoices => 'invoices',
    AdminFinanceResource.paymentAttempts => 'payment-attempts',
    AdminFinanceResource.transactions => 'transactions',
    AdminFinanceResource.refunds => 'refunds',
    AdminFinanceResource.auditLogs => 'audit-logs',
    AdminFinanceResource.ledger => 'ledger',
    AdminFinanceResource.wallets => 'wallets',
    AdminFinanceResource.settlements => 'settlements',
  };

  String get label => switch (this) {
    AdminFinanceResource.invoices => 'فاکتورها',
    AdminFinanceResource.paymentAttempts => 'تلاش‌های پرداخت',
    AdminFinanceResource.transactions => 'تراکنش‌ها',
    AdminFinanceResource.refunds => 'بازپرداخت‌ها',
    AdminFinanceResource.auditLogs => 'گزارش ممیزی',
    AdminFinanceResource.ledger => 'دفتر کل',
    AdminFinanceResource.wallets => 'حساب‌های کیف پول',
    AdminFinanceResource.settlements => 'تسویه‌ها',
  };
}

class AdminFinanceRecord {
  const AdminFinanceRecord({
    required this.id,
    required this.title,
    required this.status,
    required this.amount,
    required this.reference,
    required this.createdAt,
  });

  final int id;
  final String title;
  final String status;
  final num? amount;
  final String? reference;
  final DateTime? createdAt;

  factory AdminFinanceRecord.fromJson(
    AdminFinanceResource resource,
    Map<String, dynamic> json,
  ) {
    final title = switch (resource) {
      AdminFinanceResource.invoices =>
        json['invoice_number']?.toString() ?? 'Invoice',
      AdminFinanceResource.paymentAttempts =>
        json['provider']?.toString() ?? 'Payment',
      AdminFinanceResource.transactions =>
        json['transaction_type']?.toString() ?? 'Transaction',
      AdminFinanceResource.refunds => json['reason']?.toString() ?? 'Refund',
      AdminFinanceResource.auditLogs => json['action']?.toString() ?? 'Audit',
      AdminFinanceResource.ledger =>
        json['journal_number']?.toString() ?? 'Journal',
      AdminFinanceResource.wallets =>
        json['account_code']?.toString() ?? 'Wallet',
      AdminFinanceResource.settlements => 'Settlement #${json['id']}',
    };
    return AdminFinanceRecord(
      id: (json['id'] as num).toInt(),
      title: title,
      status:
          json['status']?.toString() ?? json['target_type']?.toString() ?? '-',
      amount:
          json['total_amount'] as num? ??
          json['total_debit'] as num? ??
          json['amount'] as num?,
      reference:
          json['provider_reference']?.toString() ??
          json['trace_id']?.toString() ??
          json['purpose']?.toString(),
      createdAt: DateTime.tryParse(
        (json['created_at'] ?? json['issued_at'] ?? json['requested_at'] ?? '')
            .toString(),
      ),
    );
  }
}

class AdminReconciliation {
  const AdminReconciliation({
    required this.clean,
    required this.missingPayments,
    required this.missingRefunds,
    required this.unbalanced,
  });
  final bool clean;
  final int missingPayments;
  final int missingRefunds;
  final int unbalanced;
  factory AdminReconciliation.fromJson(
    Map<String, dynamic> json,
  ) => AdminReconciliation(
    clean: json['is_clean'] == true,
    missingPayments:
        (json['missing_payment_transaction_ids'] as List? ?? const []).length,
    missingRefunds:
        (json['missing_refund_transaction_ids'] as List? ?? const []).length,
    unbalanced: (json['unbalanced_journal_ids'] as List? ?? const []).length,
  );
}

class AdminFinancePageResult {
  const AdminFinancePageResult({
    required this.items,
    required this.page,
    required this.totalPages,
    required this.total,
  });
  final List<AdminFinanceRecord> items;
  final int page;
  final int totalPages;
  final int total;
}
