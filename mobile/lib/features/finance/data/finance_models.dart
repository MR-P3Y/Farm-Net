class WalletBalance {
  const WalletBalance({
    required this.currency,
    required this.pending,
    required this.available,
    required this.reserved,
  });
  final String currency;
  final double pending;
  final double available;
  final double reserved;
  factory WalletBalance.fromJson(Map<String, dynamic> json) => WalletBalance(
    currency: json['currency']?.toString() ?? 'TOMAN',
    pending: (json['pending_amount'] as num?)?.toDouble() ?? 0,
    available: (json['available_amount'] as num?)?.toDouble() ?? 0,
    reserved: (json['reserved_amount'] as num?)?.toDouble() ?? 0,
  );
}

class FinanceInvoice {
  const FinanceInvoice({
    required this.id,
    required this.number,
    required this.sourceType,
    required this.status,
    required this.currency,
    required this.total,
    required this.issuedAt,
  });
  final int id;
  final String number;
  final String sourceType;
  final String status;
  final String currency;
  final double total;
  final DateTime issuedAt;
  factory FinanceInvoice.fromJson(Map<String, dynamic> json) => FinanceInvoice(
    id: (json['id'] as num).toInt(),
    number: json['invoice_number']?.toString() ?? '',
    sourceType: json['source_type']?.toString() ?? '',
    status: json['status']?.toString() ?? '',
    currency: json['currency']?.toString() ?? 'TOMAN',
    total: (json['total_amount'] as num?)?.toDouble() ?? 0,
    issuedAt: DateTime.parse(json['issued_at'].toString()),
  );
}

class Settlement {
  const Settlement({
    required this.id,
    required this.amount,
    required this.currency,
    required this.status,
    required this.requestedAt,
    this.note,
    this.adminNote,
  });
  final int id;
  final double amount;
  final String currency;
  final String status;
  final DateTime requestedAt;
  final String? note;
  final String? adminNote;
  factory Settlement.fromJson(Map<String, dynamic> json) => Settlement(
    id: (json['id'] as num).toInt(),
    amount: (json['amount'] as num).toDouble(),
    currency: json['currency']?.toString() ?? 'TOMAN',
    status: json['status']?.toString() ?? '',
    requestedAt: DateTime.parse(json['requested_at'].toString()),
    note: json['note']?.toString(),
    adminNote: json['admin_note']?.toString(),
  );
}
