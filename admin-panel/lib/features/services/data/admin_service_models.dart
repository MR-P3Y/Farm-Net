int _id(dynamic value) => (value as num?)?.toInt() ?? 0;

class AdminServicePage<T> {
  const AdminServicePage({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.total,
  });
  final List<T> items;
  final int page;
  final int pageSize;
  final int total;
  factory AdminServicePage.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) parse,
  ) {
    final meta = (json['meta'] as Map?)?.cast<String, dynamic>() ?? const {};
    return AdminServicePage(
      items:
          (json['data'] as List? ?? const [])
              .map((e) => parse((e as Map).cast<String, dynamic>()))
              .toList(),
      page: _id(meta['page']).clamp(1, 999999),
      pageSize: _id(meta['page_size']).clamp(1, 100),
      total: _id(meta['total']),
    );
  }
}

class AdminServiceCategory {
  const AdminServiceCategory({
    required this.id,
    required this.code,
    required this.title,
    required this.sortOrder,
    required this.isActive,
    this.parentId,
    this.description,
  });
  final int id;
  final int? parentId;
  final String code;
  final String title;
  final String? description;
  final int sortOrder;
  final bool isActive;
  factory AdminServiceCategory.fromJson(Map<String, dynamic> j) =>
      AdminServiceCategory(
        id: _id(j['id']),
        parentId: j['parent_id'] == null ? null : _id(j['parent_id']),
        code: j['code']?.toString() ?? '',
        title: j['title']?.toString() ?? '',
        description: j['description']?.toString(),
        sortOrder: _id(j['sort_order']),
        isActive: j['is_active'] == true,
      );
}

class AdminServiceProvider {
  const AdminServiceProvider({
    required this.id,
    required this.userId,
    required this.displayName,
    required this.status,
    required this.rating,
    required this.requestsCount,
    this.title,
    this.phone,
    this.cityName,
    this.adminNote,
  });
  final int id, userId, requestsCount;
  final String displayName, status;
  final num rating;
  final String? title, phone, cityName, adminNote;
  factory AdminServiceProvider.fromJson(Map<String, dynamic> j) =>
      AdminServiceProvider(
        id: _id(j['id']),
        userId: _id(j['user_id']),
        displayName:
            j['display_name']?.toString() ?? j['name']?.toString() ?? '',
        status: j['status']?.toString() ?? '',
        rating:
            j['rating_average'] as num? ??
            num.tryParse('${j['rating_average']}') ??
            0,
        requestsCount: _id(j['requests_count']),
        title: j['title']?.toString(),
        phone: j['phone']?.toString(),
        cityName: j['city_name']?.toString(),
        adminNote: j['admin_note']?.toString(),
      );
}

class AdminServiceOffer {
  const AdminServiceOffer({
    required this.id,
    required this.title,
    required this.status,
    required this.pricingType,
    required this.providerProfileId,
    this.categoryTitle,
    this.providerName,
    this.priceAmount,
    this.cityName,
    this.adminNote,
  });
  final int id, providerProfileId;
  final String title, status, pricingType;
  final String? categoryTitle, providerName, cityName, adminNote;
  final num? priceAmount;
  factory AdminServiceOffer.fromJson(Map<String, dynamic> j) {
    final c = j['category'] as Map?;
    final p = j['provider'] as Map?;
    return AdminServiceOffer(
      id: _id(j['id']),
      title: j['title']?.toString() ?? '',
      status: j['status']?.toString() ?? '',
      pricingType: j['pricing_type']?.toString() ?? '',
      providerProfileId: _id(j['provider_profile_id']),
      categoryTitle: c?['title']?.toString(),
      providerName: p?['display_name']?.toString() ?? p?['name']?.toString(),
      priceAmount:
          j['price_amount'] as num? ?? num.tryParse('${j['price_amount']}'),
      cityName: j['city_name']?.toString(),
      adminNote: j['admin_note']?.toString(),
    );
  }
}

class AdminServiceStatusLog {
  const AdminServiceStatusLog({
    required this.id,
    required this.requestId,
    required this.newStatus,
    required this.createdAt,
    this.changedByUserId,
    this.oldStatus,
    this.note,
  });
  final int id, requestId;
  final int? changedByUserId;
  final String? oldStatus, note;
  final String newStatus, createdAt;
  factory AdminServiceStatusLog.fromJson(Map<String, dynamic> j) =>
      AdminServiceStatusLog(
        id: _id(j['id']),
        requestId: _id(j['request_id']),
        changedByUserId:
            j['changed_by_user_id'] == null
                ? null
                : _id(j['changed_by_user_id']),
        oldStatus: j['old_status']?.toString(),
        newStatus: j['new_status']?.toString() ?? '',
        note: j['note']?.toString(),
        createdAt: j['created_at']?.toString() ?? '',
      );
}

class AdminServiceRequest {
  const AdminServiceRequest({
    required this.id,
    required this.requesterUserId,
    required this.status,
    required this.createdAt,
    this.providerUserId,
    this.offerId,
    this.categoryId,
    this.title,
    this.provinceName,
    this.cityName,
    this.description,
    this.adminNote,
    this.statusLogs = const [],
  });
  final int id, requesterUserId;
  final int? providerUserId, offerId, categoryId;
  final String status, createdAt;
  final String? title, provinceName, cityName, description, adminNote;
  final List<AdminServiceStatusLog> statusLogs;
  factory AdminServiceRequest.fromJson(Map<String, dynamic> j) =>
      AdminServiceRequest(
        id: _id(j['id']),
        requesterUserId: _id(j['requester_user_id']),
        providerUserId:
            j['provider_user_id'] == null ? null : _id(j['provider_user_id']),
        offerId: j['offer_id'] == null ? null : _id(j['offer_id']),
        categoryId: j['category_id'] == null ? null : _id(j['category_id']),
        status: j['status']?.toString() ?? '',
        createdAt: j['created_at']?.toString() ?? '',
        title: j['title']?.toString(),
        provinceName: j['province_name']?.toString(),
        cityName: j['city_name']?.toString(),
        description: j['description']?.toString(),
        adminNote: j['admin_note']?.toString(),
        statusLogs:
            (j['status_logs'] as List? ?? const [])
                .map((e) => AdminServiceStatusLog.fromJson((e as Map).cast()))
                .toList(),
      );
}
