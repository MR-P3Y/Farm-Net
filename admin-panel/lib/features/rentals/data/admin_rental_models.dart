class AdminRentalPage<T> {
  const AdminRentalPage({
    required this.items,
    required this.page,
    required this.total,
  });
  final List<T> items;
  final int page, total;
  factory AdminRentalPage.fromJson(
    Map<String, dynamic> j,
    T Function(Map<String, dynamic>) parse,
  ) => AdminRentalPage(
    items:
        (j['data'] as List? ?? const [])
            .map((e) => parse((e as Map).cast()))
            .toList(),
    page: (j['meta']?['page'] as num?)?.toInt() ?? 1,
    total: (j['meta']?['total'] as num?)?.toInt() ?? 0,
  );
}

class AdminRentalCategory {
  const AdminRentalCategory({
    required this.id,
    required this.code,
    required this.title,
    required this.sortOrder,
    required this.isActive,
    this.parentId,
    this.description,
    this.childrenCount = 0,
    this.equipmentCount = 0,
  });
  final int id;
  final int? parentId;
  final String code, title;
  final String? description;
  final int sortOrder;
  final bool isActive;
  final int childrenCount, equipmentCount;
  factory AdminRentalCategory.fromJson(Map<String, dynamic> j) =>
      AdminRentalCategory(
        id: (j['id'] as num).toInt(),
        parentId: (j['parent_id'] as num?)?.toInt(),
        code: j['code']?.toString() ?? '',
        title: j['title']?.toString() ?? '',
        description: j['description']?.toString(),
        sortOrder: (j['sort_order'] as num?)?.toInt() ?? 0,
        isActive: j['is_active'] == true,
        childrenCount: (j['children_count'] as num?)?.toInt() ?? 0,
        equipmentCount: (j['equipment_count'] as num?)?.toInt() ?? 0,
      );
}

class AdminLessorProfile {
  const AdminLessorProfile({
    required this.id,
    required this.userId,
    required this.status,
    required this.equipmentCount,
    this.displayName,
    this.phone,
    this.provinceId,
    this.cityId,
    this.addressText,
    this.adminNote,
  });
  final int id, userId, equipmentCount;
  final String status;
  final String? displayName, phone, addressText, adminNote;
  final int? provinceId, cityId;
  factory AdminLessorProfile.fromJson(Map<String, dynamic> j) =>
      AdminLessorProfile(
        id: (j['id'] as num).toInt(),
        userId: (j['user_id'] as num).toInt(),
        status: j['status']?.toString() ?? '',
        equipmentCount: (j['equipment_count'] as num?)?.toInt() ?? 0,
        displayName: j['display_name']?.toString(),
        phone: j['phone']?.toString(),
        provinceId: (j['province_id'] as num?)?.toInt(),
        cityId: (j['city_id'] as num?)?.toInt(),
        addressText: j['address_text']?.toString(),
        adminNote: j['admin_note']?.toString(),
      );
}

class AdminRentalEquipment {
  const AdminRentalEquipment({
    required this.id,
    required this.lessorProfileId,
    required this.title,
    required this.status,
    required this.operatorMode,
    required this.mediaCount,
    this.categoryId,
    this.adminNote,
  });
  final int id, lessorProfileId, mediaCount;
  final int? categoryId;
  final String title, status, operatorMode;
  final String? adminNote;
  factory AdminRentalEquipment.fromJson(Map<String, dynamic> j) =>
      AdminRentalEquipment(
        id: (j['id'] as num).toInt(),
        lessorProfileId: (j['lessor_profile_id'] as num).toInt(),
        categoryId: (j['category_id'] as num?)?.toInt(),
        title: j['title']?.toString() ?? '',
        status: j['status']?.toString() ?? '',
        operatorMode: j['operator_mode']?.toString() ?? '',
        adminNote: j['admin_note']?.toString(),
        mediaCount: (j['media'] as List? ?? const []).length,
      );
}

class AdminRentalStatusLog {
  const AdminRentalStatusLog({
    required this.id,
    required this.toStatus,
    required this.createdAt,
    this.fromStatus,
    this.note,
  });
  final int id;
  final String? fromStatus, note;
  final String toStatus, createdAt;
  factory AdminRentalStatusLog.fromJson(Map<String, dynamic> j) =>
      AdminRentalStatusLog(
        id: (j['id'] as num).toInt(),
        fromStatus: j['from_status']?.toString(),
        toStatus: j['to_status']?.toString() ?? '',
        createdAt: j['created_at']?.toString() ?? '',
        note: j['note']?.toString(),
      );
}

class AdminRentalRequest {
  const AdminRentalRequest({
    required this.id,
    required this.requesterUserId,
    required this.lessorProfileId,
    required this.equipmentId,
    required this.equipmentTitle,
    required this.status,
    required this.currency,
    this.totalAmount,
    this.adminNote,
    this.cancelReason,
    this.statusLogs = const [],
  });
  final int id, requesterUserId, lessorProfileId, equipmentId;
  final String equipmentTitle, status, currency;
  final double? totalAmount;
  final String? adminNote, cancelReason;
  final List<AdminRentalStatusLog> statusLogs;
  factory AdminRentalRequest.fromJson(Map<String, dynamic> j) =>
      AdminRentalRequest(
        id: (j['id'] as num).toInt(),
        requesterUserId: (j['requester_user_id'] as num).toInt(),
        lessorProfileId: (j['lessor_profile_id'] as num).toInt(),
        equipmentId: (j['equipment_id'] as num).toInt(),
        equipmentTitle: j['equipment_title']?.toString() ?? '',
        status: j['status']?.toString() ?? '',
        currency: j['currency']?.toString() ?? 'TOMAN',
        totalAmount: _double(j['total_amount_snapshot']),
        adminNote: j['admin_note']?.toString(),
        cancelReason: j['cancel_reason']?.toString(),
        statusLogs:
            (j['status_logs'] as List? ?? const [])
                .map((e) => AdminRentalStatusLog.fromJson((e as Map).cast()))
                .toList(),
      );
}

double? _double(Object? v) =>
    v is num ? v.toDouble() : double.tryParse(v?.toString() ?? '');
