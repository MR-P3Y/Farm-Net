enum AdminFinanceResource {
  invoices,
  paymentAttempts,
  transactions,
  refunds,
  auditLogs,
}

extension AdminFinanceResourceX on AdminFinanceResource {
  String get path => switch (this) {
    AdminFinanceResource.invoices => 'invoices',
    AdminFinanceResource.paymentAttempts => 'payment-attempts',
    AdminFinanceResource.transactions => 'transactions',
    AdminFinanceResource.refunds => 'refunds',
    AdminFinanceResource.auditLogs => 'audit-logs',
  };

  String get label => switch (this) {
    AdminFinanceResource.invoices => 'فاکتورها',
    AdminFinanceResource.paymentAttempts => 'تلاش‌های پرداخت',
    AdminFinanceResource.transactions => 'تراکنش‌ها',
    AdminFinanceResource.refunds => 'بازپرداخت‌ها',
    AdminFinanceResource.auditLogs => 'گزارش ممیزی',
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
    };
    return AdminFinanceRecord(
      id: (json['id'] as num).toInt(),
      title: title,
      status:
          json['status']?.toString() ?? json['target_type']?.toString() ?? '-',
      amount: json['total_amount'] as num? ?? json['amount'] as num?,
      reference:
          json['provider_reference']?.toString() ??
          json['trace_id']?.toString(),
      createdAt: DateTime.tryParse(
        (json['created_at'] ?? json['issued_at'] ?? '').toString(),
      ),
    );
  }
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
