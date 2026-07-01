class ConsultantProfileModel {
  const ConsultantProfileModel({
    required this.id,
    required this.userId,
    required this.status,
    required this.isVerified,
    required this.isFeatured,
    required this.ratingAverage,
    required this.reviewsCount,
    required this.requestsCount,
    required this.completedRequestsCount,
    this.displayName,
    this.name,
    this.title,
    this.bio,
    this.experienceYears,
    this.provinceName,
    this.cityName,
    this.avatarFileId,
    this.avatarMediaFileId,
    this.avatarUrl,
    this.verificationStatus,
    this.specialties = const [],
  });

  final int id;
  final int userId;
  final String? displayName;
  final String? name;
  final String? title;
  final String? bio;
  final int? experienceYears;
  final String? provinceName;
  final String? cityName;
  final String? avatarFileId;
  final int? avatarMediaFileId;
  final String? avatarUrl;
  final String status;
  final bool isVerified;
  final String? verificationStatus;
  final bool isFeatured;
  final double ratingAverage;
  final int reviewsCount;
  final int requestsCount;
  final int completedRequestsCount;
  final List<ConsultantSpecialtyModel> specialties;

  String get resolvedName {
    final primary = displayName?.trim();
    if (primary != null && primary.isNotEmpty) return primary;

    final fallback = name?.trim();
    if (fallback != null && fallback.isNotEmpty) return fallback;

    return 'مشاور';
  }

  String get locationText {
    final values =
        [provinceName, cityName]
            .where((item) => item != null && item.trim().isNotEmpty)
            .cast<String>()
            .toList();

    if (values.isEmpty) return 'موقعیت ثبت نشده';
    return values.join('، ');
  }

  factory ConsultantProfileModel.fromJson(Map<String, dynamic> json) {
    final specialtyRows = json['specialties'] as List? ?? const [];

    return ConsultantProfileModel(
      id:
          (json['id'] as num?)?.toInt() ??
          (json['consultant_id'] as num?)?.toInt() ??
          0,
      userId: (json['user_id'] as num?)?.toInt() ?? 0,
      displayName: json['display_name']?.toString(),
      name: json['name']?.toString(),
      title: json['title']?.toString(),
      bio: json['bio']?.toString(),
      experienceYears: (json['experience_years'] as num?)?.toInt(),
      provinceName: json['province_name']?.toString(),
      cityName: json['city_name']?.toString(),
      avatarFileId: json['avatar_file_id']?.toString(),
      avatarMediaFileId:
          json['avatar_media_file_id'] == null
              ? null
              : (json['avatar_media_file_id'] as num).toInt(),
      avatarUrl: json['avatar_url']?.toString(),
      status: json['status']?.toString() ?? '',
      isVerified: json['is_verified'] == true,
      verificationStatus: json['verification_status']?.toString(),
      isFeatured: json['is_featured'] == true,
      ratingAverage: (json['rating_average'] as num?)?.toDouble() ?? 0,
      reviewsCount: (json['reviews_count'] as num?)?.toInt() ?? 0,
      requestsCount: (json['requests_count'] as num?)?.toInt() ?? 0,
      completedRequestsCount:
          (json['completed_requests_count'] as num?)?.toInt() ?? 0,
      specialties:
          specialtyRows
              .whereType<Map<String, dynamic>>()
              .map(ConsultantSpecialtyModel.fromJson)
              .toList(),
    );
  }
}

class ConsultantSpecialtyModel {
  const ConsultantSpecialtyModel({
    required this.id,
    required this.code,
    required this.title,
    this.description,
  });

  final int id;
  final String code;
  final String title;
  final String? description;

  factory ConsultantSpecialtyModel.fromJson(Map<String, dynamic> json) {
    return ConsultantSpecialtyModel(
      id: (json['id'] as num?)?.toInt() ?? 0,
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString(),
    );
  }
}

class ConsultationRequestModel {
  const ConsultationRequestModel({
    required this.id,
    required this.requesterUserId,
    required this.title,
    required this.description,
    required this.contactMethod,
    required this.status,
    required this.currency,
    required this.createdAt,
    required this.updatedAt,
    this.consultantProfileId,
    this.specialtyId,
    this.budgetAmount,
    this.scheduledAt,
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
  final String contactMethod;
  final String status;
  final String? budgetAmount;
  final String currency;
  final String? scheduledAt;
  final String? consultantNote;
  final String? cancelReason;
  final String? acceptedAt;
  final String? completedAt;
  final String? cancelledAt;
  final String createdAt;
  final String updatedAt;

  final ConsultantProfileModel? consultant;
  final ConsultantSpecialtyModel? specialty;

  bool get canCancel {
    return status == 'open' || status == 'accepted' || status == 'in_progress';
  }

  factory ConsultationRequestModel.fromJson(Map<String, dynamic> json) {
    final consultantJson = json['consultant'];
    final specialtyJson = json['specialty'];

    return ConsultationRequestModel(
      id: (json['id'] as num?)?.toInt() ?? 0,
      requesterUserId: (json['requester_user_id'] as num?)?.toInt() ?? 0,
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
      contactMethod: json['contact_method']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      budgetAmount: json['budget_amount']?.toString(),
      currency: json['currency']?.toString() ?? '',
      scheduledAt: json['scheduled_at']?.toString(),
      consultantNote: json['consultant_note']?.toString(),
      cancelReason: json['cancel_reason']?.toString(),
      acceptedAt: json['accepted_at']?.toString(),
      completedAt: json['completed_at']?.toString(),
      cancelledAt: json['cancelled_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      consultant:
          consultantJson is Map<String, dynamic>
              ? ConsultantProfileModel.fromJson(consultantJson)
              : null,
      specialty:
          specialtyJson is Map<String, dynamic>
              ? ConsultantSpecialtyModel.fromJson(specialtyJson)
              : null,
    );
  }
}
