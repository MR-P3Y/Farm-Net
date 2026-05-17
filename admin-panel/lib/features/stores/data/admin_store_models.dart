class AdminStoreMember {
  const AdminStoreMember({
    required this.id,
    required this.storeId,
    required this.userId,
    required this.role,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.invitedBy,
    this.joinedAt,
  });

  final int id;
  final int storeId;
  final int userId;
  final String role;
  final String status;
  final int? invitedBy;
  final String? joinedAt;
  final String createdAt;
  final String updatedAt;

  factory AdminStoreMember.fromJson(Map<String, dynamic> json) {
    return AdminStoreMember(
      id: (json['id'] as num).toInt(),
      storeId: (json['store_id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      role: json['role']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      invitedBy:
          json['invited_by'] == null
              ? null
              : (json['invited_by'] as num).toInt(),
      joinedAt: json['joined_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class AdminStoreStatusHistory {
  const AdminStoreStatusHistory({
    required this.id,
    required this.storeId,
    required this.toStatus,
    required this.createdAt,
    this.changedBy,
    this.fromStatus,
    this.note,
  });

  final int id;
  final int storeId;
  final int? changedBy;
  final String? fromStatus;
  final String toStatus;
  final String? note;
  final String createdAt;

  factory AdminStoreStatusHistory.fromJson(Map<String, dynamic> json) {
    return AdminStoreStatusHistory(
      id: (json['id'] as num).toInt(),
      storeId: (json['store_id'] as num).toInt(),
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

class AdminStore {
  const AdminStore({
    required this.id,
    required this.ownerUserId,
    required this.name,
    required this.slug,
    required this.status,
    required this.storeType,
    required this.createdAt,
    required this.updatedAt,
    this.ownerEmail,
    this.ownerPhone,
    this.description,
    this.phone,
    this.email,
    this.provinceId,
    this.countyId,
    this.districtId,
    this.cityId,
    this.villageId,
    this.address,
    this.postalCode,
    this.latitude,
    this.longitude,
    this.logoFileId,
    this.bannerFileId,
    this.adminNote,
    this.approvedAt,
    this.approvedBy,
    this.rejectedAt,
    this.rejectedBy,
    this.members = const [],
    this.statusHistory = const [],
  });

  final int id;
  final int ownerUserId;
  final String? ownerEmail;
  final String? ownerPhone;

  final String name;
  final String slug;
  final String status;
  final String storeType;
  final String? description;

  final String? phone;
  final String? email;

  final int? provinceId;
  final int? countyId;
  final int? districtId;
  final int? cityId;
  final int? villageId;

  final String? address;
  final String? postalCode;

  final String? latitude;
  final String? longitude;

  final String? logoFileId;
  final String? bannerFileId;

  final String? adminNote;

  final String? approvedAt;
  final int? approvedBy;
  final String? rejectedAt;
  final int? rejectedBy;

  final String createdAt;
  final String updatedAt;

  final List<AdminStoreMember> members;
  final List<AdminStoreStatusHistory> statusHistory;

  factory AdminStore.fromJson(Map<String, dynamic> json) {
    final members = json['members'] as List? ?? [];
    final history = json['status_history'] as List? ?? [];

    return AdminStore(
      id: (json['id'] as num).toInt(),
      ownerUserId: (json['owner_user_id'] as num).toInt(),
      ownerEmail: json['owner_email']?.toString(),
      ownerPhone: json['owner_phone']?.toString(),
      name: json['name']?.toString() ?? '',
      slug: json['slug']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      storeType: json['store_type']?.toString() ?? '',
      description: json['description']?.toString(),
      phone: json['phone']?.toString(),
      email: json['email']?.toString(),
      provinceId:
          json['province_id'] == null
              ? null
              : (json['province_id'] as num).toInt(),
      countyId:
          json['county_id'] == null ? null : (json['county_id'] as num).toInt(),
      districtId:
          json['district_id'] == null
              ? null
              : (json['district_id'] as num).toInt(),
      cityId: json['city_id'] == null ? null : (json['city_id'] as num).toInt(),
      villageId:
          json['village_id'] == null
              ? null
              : (json['village_id'] as num).toInt(),
      address: json['address']?.toString(),
      postalCode: json['postal_code']?.toString(),
      latitude: json['latitude']?.toString(),
      longitude: json['longitude']?.toString(),
      logoFileId: json['logo_file_id']?.toString(),
      bannerFileId: json['banner_file_id']?.toString(),
      adminNote: json['admin_note']?.toString(),
      approvedAt: json['approved_at']?.toString(),
      approvedBy:
          json['approved_by'] == null
              ? null
              : (json['approved_by'] as num).toInt(),
      rejectedAt: json['rejected_at']?.toString(),
      rejectedBy:
          json['rejected_by'] == null
              ? null
              : (json['rejected_by'] as num).toInt(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      members:
          members
              .map((item) => AdminStoreMember.fromJson((item as Map).cast()))
              .toList(),
      statusHistory:
          history
              .map(
                (item) =>
                    AdminStoreStatusHistory.fromJson((item as Map).cast()),
              )
              .toList(),
    );
  }
}
