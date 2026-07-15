class AdminConsultSpecialty {
  const AdminConsultSpecialty({
    required this.id,
    required this.code,
    required this.title,
    required this.sortOrder,
    required this.isActive,
    this.description,
  });

  final int id;
  final String code;
  final String title;
  final String? description;
  final int sortOrder;
  final bool isActive;

  factory AdminConsultSpecialty.fromJson(Map<String, dynamic> json) {
    return AdminConsultSpecialty(
      id: (json['id'] as num).toInt(),
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString(),
      sortOrder: (json['sort_order'] as num?)?.toInt() ?? 100,
      isActive: json['is_active'] == true,
    );
  }
}

class AdminConsultProfile {
  const AdminConsultProfile({
    required this.id,
    required this.userId,
    required this.status,
    required this.isVerified,
    required this.ratingAverage,
    required this.reviewsCount,
    required this.requestsCount,
    required this.completedRequestsCount,
    required this.specialties,
    this.displayName,
    this.title,
    this.bio,
    this.avatarUrl,
    this.provinceName,
    this.cityName,
    this.adminNote,
  });

  final int id;
  final int userId;
  final String? displayName;
  final String? title;
  final String? bio;
  final String? avatarUrl;
  final String? provinceName;
  final String? cityName;
  final String status;
  final bool isVerified;
  final String ratingAverage;
  final int reviewsCount;
  final int requestsCount;
  final int completedRequestsCount;
  final String? adminNote;
  final List<AdminConsultSpecialty> specialties;

  factory AdminConsultProfile.fromJson(Map<String, dynamic> json) {
    final specialties = json['specialties'] as List? ?? [];

    return AdminConsultProfile(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      displayName: json['display_name']?.toString() ?? json['name']?.toString(),
      title: json['title']?.toString(),
      bio: json['bio']?.toString(),
      avatarUrl: json['avatar_url']?.toString(),
      provinceName: json['province_name']?.toString(),
      cityName: json['city_name']?.toString(),
      status: json['status']?.toString() ?? '',
      isVerified: json['is_verified'] == true,
      ratingAverage: json['rating_average']?.toString() ?? '0',
      reviewsCount: (json['reviews_count'] as num?)?.toInt() ?? 0,
      requestsCount: (json['requests_count'] as num?)?.toInt() ?? 0,
      completedRequestsCount:
          (json['completed_requests_count'] as num?)?.toInt() ?? 0,
      adminNote: json['admin_note']?.toString(),
      specialties:
          specialties
              .map(
                (item) => AdminConsultSpecialty.fromJson(
                  (item as Map).cast<String, dynamic>(),
                ),
              )
              .toList(),
    );
  }

  String get specialtyText {
    if (specialties.isEmpty) return '-';
    return specialties.map((item) => item.title).join('، ');
  }
}

class AdminConsultRequest {
  const AdminConsultRequest({
    required this.id,
    required this.requesterUserId,
    required this.title,
    required this.description,
    required this.status,
    required this.contactMethod,
    required this.currency,
    required this.createdAt,
    required this.updatedAt,
    required this.statusLogs,
    this.consultantProfileId,
    this.specialtyId,
    this.budgetAmount,
    this.scheduledAt,
    this.adminNote,
    this.consultantNote,
    this.cancelReason,
    this.acceptedAt,
    this.completedAt,
    this.cancelledAt,
    this.consultant,
    this.specialty,
  });

  final int id;
  final int requesterUserId;
  final int? consultantProfileId;
  final int? specialtyId;
  final String title;
  final String description;
  final String status;
  final String contactMethod;
  final String? budgetAmount;
  final String currency;
  final String? scheduledAt;
  final String? adminNote;
  final String? consultantNote;
  final String? cancelReason;
  final String? acceptedAt;
  final String? completedAt;
  final String? cancelledAt;
  final String createdAt;
  final String updatedAt;
  final AdminConsultProfile? consultant;
  final AdminConsultSpecialty? specialty;
  final List<AdminConsultRequestStatusLog> statusLogs;

  factory AdminConsultRequest.fromJson(Map<String, dynamic> json) {
    final logs = json['status_logs'] as List? ?? [];

    return AdminConsultRequest(
      id: (json['id'] as num).toInt(),
      requesterUserId: (json['requester_user_id'] as num).toInt(),
      consultantProfileId:
          json['consultant_profile_id'] == null
              ? null
              : (json['consultant_profile_id'] as num).toInt(),
      specialtyId:
          json['specialty_id'] == null
              ? null
              : (json['specialty_id'] as num).toInt(),
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      contactMethod: json['contact_method']?.toString() ?? '',
      budgetAmount: json['budget_amount']?.toString(),
      currency: json['currency']?.toString() ?? 'IRR',
      scheduledAt: json['scheduled_at']?.toString(),
      adminNote: json['admin_note']?.toString(),
      consultantNote: json['consultant_note']?.toString(),
      cancelReason: json['cancel_reason']?.toString(),
      acceptedAt: json['accepted_at']?.toString(),
      completedAt: json['completed_at']?.toString(),
      cancelledAt: json['cancelled_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      consultant:
          json['consultant'] is Map
              ? AdminConsultProfile.fromJson(
                (json['consultant'] as Map).cast<String, dynamic>(),
              )
              : null,
      specialty:
          json['specialty'] is Map
              ? AdminConsultSpecialty.fromJson(
                (json['specialty'] as Map).cast<String, dynamic>(),
              )
              : null,
      statusLogs:
          logs
              .map(
                (item) => AdminConsultRequestStatusLog.fromJson(
                  (item as Map).cast<String, dynamic>(),
                ),
              )
              .toList(),
    );
  }
}

class AdminConsultRequestStatusLog {
  const AdminConsultRequestStatusLog({
    required this.id,
    required this.toStatus,
    required this.createdAt,
    this.fromStatus,
    this.changedBy,
    this.note,
  });

  final int id;
  final int? changedBy;
  final String? fromStatus;
  final String toStatus;
  final String? note;
  final String createdAt;

  factory AdminConsultRequestStatusLog.fromJson(Map<String, dynamic> json) {
    return AdminConsultRequestStatusLog(
      id: (json['id'] as num).toInt(),
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
