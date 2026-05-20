num numFromJson(dynamic value) {
  if (value is num) return value;
  if (value is String) return num.tryParse(value) ?? 0;
  return 0;
}

class AdminOrderItem {
  const AdminOrderItem({
    required this.id,
    required this.orderId,
    required this.productId,
    required this.storeId,
    required this.quantity,
    required this.unitPrice,
    required this.lineTotal,
    required this.productNameSnapshot,
    required this.productSlugSnapshot,
    required this.unitSnapshot,
    required this.createdAt,
    this.productSkuSnapshot,
  });

  final int id;
  final int orderId;
  final int productId;
  final int storeId;
  final int quantity;
  final num unitPrice;
  final num lineTotal;
  final String productNameSnapshot;
  final String productSlugSnapshot;
  final String? productSkuSnapshot;
  final String unitSnapshot;
  final String createdAt;

  factory AdminOrderItem.fromJson(Map<String, dynamic> json) {
    return AdminOrderItem(
      id: (json['id'] as num).toInt(),
      orderId: (json['order_id'] as num).toInt(),
      productId: (json['product_id'] as num).toInt(),
      storeId: (json['store_id'] as num).toInt(),
      quantity: (json['quantity'] as num).toInt(),
      unitPrice: numFromJson(json['unit_price']),
      lineTotal: numFromJson(json['line_total']),
      productNameSnapshot: json['product_name_snapshot']?.toString() ?? '',
      productSlugSnapshot: json['product_slug_snapshot']?.toString() ?? '',
      productSkuSnapshot: json['product_sku_snapshot']?.toString(),
      unitSnapshot: json['unit_snapshot']?.toString() ?? '',
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminPayment {
  const AdminPayment({
    required this.id,
    required this.orderId,
    required this.userId,
    required this.method,
    required this.status,
    required this.amount,
    required this.currency,
    required this.createdAt,
    required this.updatedAt,
    this.provider,
    this.providerPaymentId,
    this.providerReference,
    this.paidAt,
    this.failedAt,
    this.cancelledAt,
  });

  final int id;
  final int orderId;
  final int userId;
  final String method;
  final String status;
  final num amount;
  final String currency;
  final String? provider;
  final String? providerPaymentId;
  final String? providerReference;
  final String? paidAt;
  final String? failedAt;
  final String? cancelledAt;
  final String createdAt;
  final String updatedAt;

  factory AdminPayment.fromJson(Map<String, dynamic> json) {
    return AdminPayment(
      id: (json['id'] as num).toInt(),
      orderId: (json['order_id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      method: json['method']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      amount: numFromJson(json['amount']),
      currency: json['currency']?.toString() ?? 'TOMAN',
      provider: json['provider']?.toString(),
      providerPaymentId: json['provider_payment_id']?.toString(),
      providerReference: json['provider_reference']?.toString(),
      paidAt: json['paid_at']?.toString(),
      failedAt: json['failed_at']?.toString(),
      cancelledAt: json['cancelled_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class AdminOrderHistory {
  const AdminOrderHistory({
    required this.id,
    required this.orderId,
    required this.toStatus,
    required this.createdAt,
    this.changedBy,
    this.fromStatus,
    this.note,
  });

  final int id;
  final int orderId;
  final int? changedBy;
  final String? fromStatus;
  final String toStatus;
  final String? note;
  final String createdAt;

  factory AdminOrderHistory.fromJson(Map<String, dynamic> json) {
    return AdminOrderHistory(
      id: (json['id'] as num).toInt(),
      orderId: (json['order_id'] as num).toInt(),
      changedBy:
          json['changed_by'] == null
              ? null
              : (json['changed_by'] as num).toInt(),
      fromStatus: json['from_status']?.toString(),
      toStatus: json['to_status']?.toString() ?? '',
      note: json['note']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminOrder {
  const AdminOrder({
    required this.id,
    required this.orderNumber,
    required this.buyerUserId,
    required this.storeId,
    required this.status,
    required this.paymentStatus,
    required this.currency,
    required this.subtotalAmount,
    required this.discountAmount,
    required this.shippingAmount,
    required this.totalAmount,
    required this.commissionPercent,
    required this.commissionAmount,
    required this.sellerAmount,
    required this.createdAt,
    required this.updatedAt,
    this.buyerNote,
    this.sellerNote,
    this.adminNote,
    this.shippingAddress,
    this.shippingPostalCode,
    this.shippingPhone,
    this.paidAt,
    this.confirmedAt,
    this.cancelledAt,
    this.deliveredAt,
    this.items = const [],
    this.payments = const [],
    this.statusHistory = const [],
  });

  final int id;
  final String orderNumber;
  final int buyerUserId;
  final int storeId;
  final String status;
  final String paymentStatus;
  final String currency;
  final num subtotalAmount;
  final num discountAmount;
  final num shippingAmount;
  final num totalAmount;
  final num commissionPercent;
  final num commissionAmount;
  final num sellerAmount;
  final String? buyerNote;
  final String? sellerNote;
  final String? adminNote;
  final String? shippingAddress;
  final String? shippingPostalCode;
  final String? shippingPhone;
  final String? paidAt;
  final String? confirmedAt;
  final String? cancelledAt;
  final String? deliveredAt;
  final String createdAt;
  final String updatedAt;
  final List<AdminOrderItem> items;
  final List<AdminPayment> payments;
  final List<AdminOrderHistory> statusHistory;

  factory AdminOrder.fromJson(Map<String, dynamic> json) {
    final itemRows = json['items'] as List? ?? [];
    final paymentRows = json['payments'] as List? ?? [];
    final historyRows = json['status_history'] as List? ?? [];

    return AdminOrder(
      id: (json['id'] as num).toInt(),
      orderNumber: json['order_number']?.toString() ?? '',
      buyerUserId: (json['buyer_user_id'] as num).toInt(),
      storeId: (json['store_id'] as num).toInt(),
      status: json['status']?.toString() ?? '',
      paymentStatus: json['payment_status']?.toString() ?? '',
      currency: json['currency']?.toString() ?? 'TOMAN',
      subtotalAmount: numFromJson(json['subtotal_amount']),
      discountAmount: numFromJson(json['discount_amount']),
      shippingAmount: numFromJson(json['shipping_amount']),
      totalAmount: numFromJson(json['total_amount']),
      commissionPercent: numFromJson(json['commission_percent']),
      commissionAmount: numFromJson(json['commission_amount']),
      sellerAmount: numFromJson(json['seller_amount']),
      buyerNote: json['buyer_note']?.toString(),
      sellerNote: json['seller_note']?.toString(),
      adminNote: json['admin_note']?.toString(),
      shippingAddress: json['shipping_address']?.toString(),
      shippingPostalCode: json['shipping_postal_code']?.toString(),
      shippingPhone: json['shipping_phone']?.toString(),
      paidAt: json['paid_at']?.toString(),
      confirmedAt: json['confirmed_at']?.toString(),
      cancelledAt: json['cancelled_at']?.toString(),
      deliveredAt: json['delivered_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      items:
          itemRows
              .map((item) => AdminOrderItem.fromJson((item as Map).cast()))
              .toList(),
      payments:
          paymentRows
              .map((item) => AdminPayment.fromJson((item as Map).cast()))
              .toList(),
      statusHistory:
          historyRows
              .map((item) => AdminOrderHistory.fromJson((item as Map).cast()))
              .toList(),
    );
  }
}
