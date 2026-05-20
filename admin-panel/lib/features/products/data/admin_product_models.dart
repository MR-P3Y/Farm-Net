class AdminProductImage {
  const AdminProductImage({
    required this.id,
    required this.productId,
    required this.filePath,
    required this.sortOrder,
    required this.isPrimary,
    required this.createdAt,
    required this.updatedAt,
    this.fileId,
    this.altText,
  });

  final int id;
  final int productId;
  final String? fileId;
  final String filePath;
  final String? altText;
  final int sortOrder;
  final bool isPrimary;
  final String createdAt;
  final String updatedAt;

  factory AdminProductImage.fromJson(Map<String, dynamic> json) {
    return AdminProductImage(
      id: (json['id'] as num).toInt(),
      productId: (json['product_id'] as num).toInt(),
      fileId: json['file_id']?.toString(),
      filePath: json['file_path']?.toString() ?? '',
      altText: json['alt_text']?.toString(),
      sortOrder: (json['sort_order'] as num?)?.toInt() ?? 0,
      isPrimary: json['is_primary'] == true,
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class AdminProductStatusHistory {
  const AdminProductStatusHistory({
    required this.id,
    required this.productId,
    required this.toStatus,
    required this.createdAt,
    this.changedBy,
    this.fromStatus,
    this.note,
  });

  final int id;
  final int productId;
  final int? changedBy;
  final String? fromStatus;
  final String toStatus;
  final String? note;
  final String createdAt;

  factory AdminProductStatusHistory.fromJson(Map<String, dynamic> json) {
    return AdminProductStatusHistory(
      id: (json['id'] as num).toInt(),
      productId: (json['product_id'] as num).toInt(),
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

class AdminProduct {
  const AdminProduct({
    required this.id,
    required this.storeId,
    required this.name,
    required this.slug,
    required this.status,
    required this.price,
    required this.currency,
    required this.stockQuantity,
    required this.unit,
    required this.minOrderQuantity,
    required this.isActive,
    required this.isFeatured,
    required this.createdAt,
    required this.updatedAt,
    this.storeName,
    this.storeSlug,
    this.ownerUserId,
    this.ownerEmail,
    this.ownerPhone,
    this.categoryId,
    this.categoryName,
    this.categorySlug,
    this.shortDescription,
    this.description,
    this.sku,
    this.compareAtPrice,
    this.maxOrderQuantity,
    this.adminNote,
    this.suspendedAt,
    this.suspendedBy,
    this.deletedAt,
    this.images = const [],
    this.statusHistory = const [],
  });

  final int id;
  final int storeId;
  final String? storeName;
  final String? storeSlug;
  final int? ownerUserId;
  final String? ownerEmail;
  final String? ownerPhone;
  final int? categoryId;
  final String? categoryName;
  final String? categorySlug;
  final String name;
  final String slug;
  final String? shortDescription;
  final String? description;
  final String? sku;
  final String status;
  final num price;
  final num? compareAtPrice;
  final String currency;
  final int stockQuantity;
  final String unit;
  final int minOrderQuantity;
  final int? maxOrderQuantity;
  final bool isActive;
  final bool isFeatured;
  final String? adminNote;
  final String? suspendedAt;
  final int? suspendedBy;
  final String createdAt;
  final String updatedAt;
  final String? deletedAt;
  final List<AdminProductImage> images;
  final List<AdminProductStatusHistory> statusHistory;

  factory AdminProduct.fromJson(Map<String, dynamic> json) {
    final imageRows = json['images'] as List? ?? [];
    final historyRows = json['status_history'] as List? ?? [];

    return AdminProduct(
      id: (json['id'] as num).toInt(),
      storeId: (json['store_id'] as num).toInt(),
      storeName: json['store_name']?.toString(),
      storeSlug: json['store_slug']?.toString(),
      ownerUserId:
          json['owner_user_id'] == null
              ? null
              : (json['owner_user_id'] as num).toInt(),
      ownerEmail: json['owner_email']?.toString(),
      ownerPhone: json['owner_phone']?.toString(),
      categoryId:
          json['category_id'] == null
              ? null
              : (json['category_id'] as num).toInt(),
      categoryName: json['category_name']?.toString(),
      categorySlug: json['category_slug']?.toString(),
      name: json['name']?.toString() ?? '',
      slug: json['slug']?.toString() ?? '',
      shortDescription: json['short_description']?.toString(),
      description: json['description']?.toString(),
      sku: json['sku']?.toString(),
      status: json['status']?.toString() ?? '',
      price: _numFromJson(json['price']),
      compareAtPrice:
          json['compare_at_price'] == null
              ? null
              : _numFromJson(json['compare_at_price']),
      currency: json['currency']?.toString() ?? 'TOMAN',
      stockQuantity: (json['stock_quantity'] as num?)?.toInt() ?? 0,
      unit: json['unit']?.toString() ?? 'piece',
      minOrderQuantity: (json['min_order_quantity'] as num?)?.toInt() ?? 1,
      maxOrderQuantity:
          json['max_order_quantity'] == null
              ? null
              : (json['max_order_quantity'] as num).toInt(),
      isActive: json['is_active'] != false,
      isFeatured: json['is_featured'] == true,
      adminNote: json['admin_note']?.toString(),
      suspendedAt: json['suspended_at']?.toString(),
      suspendedBy:
          json['suspended_by'] == null
              ? null
              : (json['suspended_by'] as num).toInt(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      deletedAt: json['deleted_at']?.toString(),
      images:
          imageRows
              .map((item) => AdminProductImage.fromJson((item as Map).cast()))
              .toList(),
      statusHistory:
          historyRows
              .map(
                (item) =>
                    AdminProductStatusHistory.fromJson((item as Map).cast()),
              )
              .toList(),
    );
  }

  static num _numFromJson(dynamic value) {
    if (value is num) return value;
    if (value is String) return num.tryParse(value) ?? 0;
    return 0;
  }
}
