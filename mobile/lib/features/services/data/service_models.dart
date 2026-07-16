class ServiceCategory {
  const ServiceCategory({
    required this.id,
    required this.title,
    this.description,
  });

  final int id;
  final String title;
  final String? description;

  factory ServiceCategory.fromJson(Map<String, dynamic> json) =>
      ServiceCategory(
        id: (json['id'] as num?)?.toInt() ?? 0,
        title: json['title']?.toString() ?? '',
        description: json['description']?.toString(),
      );
}

class ServiceMedia {
  const ServiceMedia({
    required this.id,
    this.mediaFileId,
    this.publicUrl,
    this.filePath,
    this.altText,
    this.isPrimary = false,
  });

  final int id;
  final int? mediaFileId;
  final String? publicUrl;
  final String? filePath;
  final String? altText;
  final bool isPrimary;

  String? get displayUrl => publicUrl ?? filePath;

  factory ServiceMedia.fromJson(Map<String, dynamic> json) => ServiceMedia(
    id: (json['id'] as num?)?.toInt() ?? 0,
    mediaFileId: (json['media_file_id'] as num?)?.toInt(),
    publicUrl: json['public_url']?.toString(),
    filePath: json['file_path']?.toString(),
    altText: json['alt_text']?.toString(),
    isPrimary: json['is_primary'] == true,
  );
}

class ServiceProviderSummary {
  const ServiceProviderSummary({
    required this.id,
    required this.isVerified,
    required this.completedRequestsCount,
    this.displayName,
    this.name,
    this.title,
    this.bio,
    this.provinceName,
    this.cityName,
    this.avatarUrl,
  });

  final int id;
  final String? displayName;
  final String? name;
  final String? title;
  final String? bio;
  final String? provinceName;
  final String? cityName;
  final String? avatarUrl;
  final bool isVerified;
  final int completedRequestsCount;

  String get resolvedName =>
      (displayName?.trim().isNotEmpty ?? false)
          ? displayName!.trim()
          : (name?.trim().isNotEmpty ?? false)
          ? name!.trim()
          : 'خدمات‌دهنده';

  String get location => [
    provinceName,
    cityName,
  ].where((value) => value?.trim().isNotEmpty ?? false).join('، ');

  factory ServiceProviderSummary.fromJson(Map<String, dynamic> json) =>
      ServiceProviderSummary(
        id: (json['id'] as num?)?.toInt() ?? 0,
        displayName: json['display_name']?.toString(),
        name: json['name']?.toString(),
        title: json['title']?.toString(),
        bio: json['bio']?.toString(),
        provinceName: json['province_name']?.toString(),
        cityName: json['city_name']?.toString(),
        avatarUrl: json['avatar_url']?.toString(),
        isVerified: json['is_verified'] == true,
        completedRequestsCount:
            (json['completed_requests_count'] as num?)?.toInt() ?? 0,
      );
}

class ServiceOffer {
  const ServiceOffer({
    required this.id,
    required this.providerProfileId,
    required this.title,
    required this.pricingType,
    required this.currency,
    required this.media,
    this.categoryId,
    this.slug,
    this.shortDescription,
    this.description,
    this.priceAmount,
    this.provinceName,
    this.cityName,
    this.serviceArea,
    this.category,
    this.provider,
    this.primaryMedia,
  });

  final int id;
  final int providerProfileId;
  final int? categoryId;
  final String title;
  final String? slug;
  final String? shortDescription;
  final String? description;
  final String pricingType;
  final double? priceAmount;
  final String currency;
  final String? provinceName;
  final String? cityName;
  final String? serviceArea;
  final ServiceCategory? category;
  final ServiceProviderSummary? provider;
  final List<ServiceMedia> media;
  final ServiceMedia? primaryMedia;

  String get location => [
    provinceName,
    cityName,
  ].where((value) => value?.trim().isNotEmpty ?? false).join('، ');

  factory ServiceOffer.fromJson(Map<String, dynamic> json) {
    final media =
        (json['media'] as List? ?? const [])
            .whereType<Map<String, dynamic>>()
            .map(ServiceMedia.fromJson)
            .toList();
    final primaryJson = json['primary_media'];
    return ServiceOffer(
      id: (json['id'] as num?)?.toInt() ?? 0,
      providerProfileId: (json['provider_profile_id'] as num?)?.toInt() ?? 0,
      categoryId: (json['category_id'] as num?)?.toInt(),
      title: json['title']?.toString() ?? '',
      slug: json['slug']?.toString(),
      shortDescription: json['short_description']?.toString(),
      description: json['description']?.toString(),
      pricingType: json['pricing_type']?.toString() ?? 'negotiable',
      priceAmount: _toDouble(json['price_amount']),
      currency: json['currency']?.toString() ?? 'TOMAN',
      provinceName: json['province_name']?.toString(),
      cityName: json['city_name']?.toString(),
      serviceArea: json['service_area']?.toString(),
      category:
          json['category'] is Map<String, dynamic>
              ? ServiceCategory.fromJson(
                json['category'] as Map<String, dynamic>,
              )
              : null,
      provider:
          json['provider'] is Map<String, dynamic>
              ? ServiceProviderSummary.fromJson(
                json['provider'] as Map<String, dynamic>,
              )
              : null,
      media: media,
      primaryMedia:
          primaryJson is Map<String, dynamic>
              ? ServiceMedia.fromJson(primaryJson)
              : media.where((item) => item.isPrimary).firstOrNull,
    );
  }
}

double? _toDouble(Object? value) {
  if (value is num) return value.toDouble();
  return double.tryParse(value?.toString() ?? '');
}

class ServiceRequestStatusLog {
  const ServiceRequestStatusLog({
    required this.id,
    required this.newStatus,
    required this.createdAt,
    this.oldStatus,
    this.note,
  });
  final int id;
  final String? oldStatus;
  final String newStatus;
  final String createdAt;
  final String? note;
  factory ServiceRequestStatusLog.fromJson(Map<String, dynamic> json) =>
      ServiceRequestStatusLog(
        id: (json['id'] as num?)?.toInt() ?? 0,
        oldStatus: json['old_status']?.toString(),
        newStatus: json['new_status']?.toString() ?? '',
        createdAt: json['created_at']?.toString() ?? '',
        note: json['note']?.toString(),
      );
}

class ServiceRequest {
  const ServiceRequest({
    required this.id,
    required this.title,
    required this.status,
    required this.currency,
    required this.createdAt,
    this.offerId,
    this.offerTitle,
    this.categoryTitle,
    this.providerDisplayName,
    this.description,
    this.contactMethod,
    this.budgetAmount,
    this.scheduledAt,
    this.provinceName,
    this.cityName,
    this.addressText,
    this.providerNote,
    this.cancelReason,
    this.acceptedAt,
    this.completedAt,
    this.cancelledAt,
    this.statusLogs = const [],
  });
  final int id;
  final int? offerId;
  final String? offerTitle;
  final String? categoryTitle;
  final String? providerDisplayName;
  final String title;
  final String status;
  final String currency;
  final String createdAt;
  final String? description;
  final String? contactMethod;
  final double? budgetAmount;
  final String? scheduledAt;
  final String? provinceName;
  final String? cityName;
  final String? addressText;
  final String? providerNote;
  final String? cancelReason;
  final String? acceptedAt;
  final String? completedAt;
  final String? cancelledAt;
  final List<ServiceRequestStatusLog> statusLogs;

  bool get canCancel => status == 'open' || status == 'accepted';

  factory ServiceRequest.fromJson(Map<String, dynamic> json) => ServiceRequest(
    id: (json['id'] as num?)?.toInt() ?? 0,
    offerId: (json['offer_id'] as num?)?.toInt(),
    offerTitle: json['offer_title']?.toString(),
    categoryTitle: json['category_title']?.toString(),
    providerDisplayName: json['provider_display_name']?.toString(),
    title: json['title']?.toString() ?? '',
    status: json['status']?.toString() ?? '',
    currency: json['currency']?.toString() ?? 'TOMAN',
    createdAt: json['created_at']?.toString() ?? '',
    description: json['description']?.toString(),
    contactMethod: json['contact_method']?.toString(),
    budgetAmount: _toDouble(json['budget_amount']),
    scheduledAt: json['scheduled_at']?.toString(),
    provinceName: json['province_name']?.toString(),
    cityName: json['city_name']?.toString(),
    addressText: json['address_text']?.toString(),
    providerNote: json['provider_note']?.toString(),
    cancelReason: json['cancel_reason']?.toString(),
    acceptedAt: json['accepted_at']?.toString(),
    completedAt: json['completed_at']?.toString(),
    cancelledAt: json['cancelled_at']?.toString(),
    statusLogs:
        (json['status_logs'] as List? ?? const [])
            .whereType<Map<String, dynamic>>()
            .map(ServiceRequestStatusLog.fromJson)
            .toList(),
  );
}

class ServiceRequestInput {
  const ServiceRequestInput({
    required this.offerId,
    required this.title,
    required this.description,
    required this.contactMethod,
    this.budgetAmount,
    this.scheduledAt,
    this.provinceId,
    this.cityId,
    this.provinceName,
    this.cityName,
    this.addressText,
  });
  final int offerId;
  final String title;
  final String description;
  final String contactMethod;
  final double? budgetAmount;
  final String? scheduledAt;
  final int? provinceId;
  final int? cityId;
  final String? provinceName;
  final String? cityName;
  final String? addressText;
  Map<String, dynamic> toJson() => {
    'offer_id': offerId,
    'title': title,
    'description': description,
    'contact_method': contactMethod,
    'currency': 'TOMAN',
    if (budgetAmount != null) 'budget_amount': budgetAmount,
    if (scheduledAt != null) 'scheduled_at': scheduledAt,
    if (provinceId != null) 'province_id': provinceId,
    if (cityId != null) 'city_id': cityId,
    if (provinceName != null) 'province_name': provinceName,
    if (cityName != null) 'city_name': cityName,
    if (addressText?.trim().isNotEmpty ?? false)
      'address_text': addressText!.trim(),
  };
}

String serviceStatusLabel(String status) =>
    const {
      'draft': 'پیش‌نویس',
      'pending_review': 'در انتظار بررسی',
      'approved': 'تأییدشده',
      'rejected': 'ردشده',
      'suspended': 'تعلیق‌شده',
      'archived': 'بایگانی‌شده',
    }[status] ??
    status;

class ServiceProviderProfileOwner {
  const ServiceProviderProfileOwner({
    required this.id,
    required this.userId,
    required this.status,
    this.displayName,
    this.title,
    this.bio,
    this.experienceYears,
    this.phone,
    this.email,
    this.provinceId,
    this.cityId,
    this.provinceName,
    this.cityName,
    this.serviceArea,
    this.avatarMediaFileId,
    this.avatarUrl,
    this.categories = const [],
    this.adminNote,
  });
  final int id;
  final int userId;
  final String status;
  final String? displayName;
  final String? title;
  final String? bio;
  final int? experienceYears;
  final String? phone;
  final String? email;
  final int? provinceId;
  final int? cityId;
  final String? provinceName;
  final String? cityName;
  final String? serviceArea;
  final int? avatarMediaFileId;
  final String? avatarUrl;
  final List<ServiceCategory> categories;
  final String? adminNote;
  bool get canEdit => status != 'suspended';
  bool get canSubmit => status == 'draft' || status == 'rejected';
  bool get isApproved => status == 'approved';
  String get statusLabelFa => serviceStatusLabel(status);
  factory ServiceProviderProfileOwner.fromJson(Map<String, dynamic> json) =>
      ServiceProviderProfileOwner(
        id: (json['id'] as num?)?.toInt() ?? 0,
        userId: (json['user_id'] as num?)?.toInt() ?? 0,
        status: json['status']?.toString() ?? 'draft',
        displayName: json['display_name']?.toString(),
        title: json['title']?.toString(),
        bio: json['bio']?.toString(),
        experienceYears: (json['experience_years'] as num?)?.toInt(),
        phone: json['phone']?.toString(),
        email: json['email']?.toString(),
        provinceId: (json['province_id'] as num?)?.toInt(),
        cityId: (json['city_id'] as num?)?.toInt(),
        provinceName: json['province_name']?.toString(),
        cityName: json['city_name']?.toString(),
        serviceArea: json['service_area']?.toString(),
        avatarMediaFileId: (json['avatar_media_file_id'] as num?)?.toInt(),
        avatarUrl: json['avatar_url']?.toString(),
        categories:
            (json['categories'] as List? ?? const [])
                .whereType<Map<String, dynamic>>()
                .map(ServiceCategory.fromJson)
                .toList(),
        adminNote: json['admin_note']?.toString(),
      );
}

class ServiceProviderProfileInput {
  const ServiceProviderProfileInput({
    required this.categoryIds,
    this.displayName,
    this.title,
    this.bio,
    this.experienceYears,
    this.phone,
    this.email,
    this.provinceId,
    this.cityId,
    this.provinceName,
    this.cityName,
    this.serviceArea,
    this.avatarMediaFileId,
  });
  final List<int> categoryIds;
  final String? displayName;
  final String? title;
  final String? bio;
  final int? experienceYears;
  final String? phone;
  final String? email;
  final int? provinceId;
  final int? cityId;
  final String? provinceName;
  final String? cityName;
  final String? serviceArea;
  final int? avatarMediaFileId;
  Map<String, dynamic> toJson() => {
    'display_name': displayName,
    'title': title,
    'bio': bio,
    'experience_years': experienceYears,
    'phone': phone,
    'email': email,
    'province_id': provinceId,
    'city_id': cityId,
    'province_name': provinceName,
    'city_name': cityName,
    'service_area': serviceArea,
    'avatar_media_file_id': avatarMediaFileId,
    'category_ids': categoryIds,
  };
}

class ServiceOfferOwner extends ServiceOffer {
  const ServiceOfferOwner({
    required super.id,
    required super.providerProfileId,
    required super.title,
    required super.pricingType,
    required super.currency,
    required super.media,
    required this.status,
    super.categoryId,
    super.slug,
    super.shortDescription,
    super.description,
    super.priceAmount,
    super.provinceName,
    super.cityName,
    super.serviceArea,
    super.category,
    super.provider,
    super.primaryMedia,
    this.adminNote,
  });
  final String status;
  final String? adminNote;
  bool get canEdit => status != 'suspended' && status != 'archived';
  bool get canSubmit => status == 'draft' || status == 'rejected';
  String get statusLabelFa => serviceStatusLabel(status);
  factory ServiceOfferOwner.fromJson(Map<String, dynamic> json) {
    final base = ServiceOffer.fromJson(json);
    return ServiceOfferOwner(
      id: base.id,
      providerProfileId: base.providerProfileId,
      title: base.title,
      pricingType: base.pricingType,
      currency: base.currency,
      media: base.media,
      status: json['status']?.toString() ?? 'draft',
      categoryId: base.categoryId,
      slug: base.slug,
      shortDescription: base.shortDescription,
      description: base.description,
      priceAmount: base.priceAmount,
      provinceName: base.provinceName,
      cityName: base.cityName,
      serviceArea: base.serviceArea,
      category: base.category,
      provider: base.provider,
      primaryMedia: base.primaryMedia,
      adminNote: json['admin_note']?.toString(),
    );
  }
}

class ServiceOfferInput {
  const ServiceOfferInput({
    required this.title,
    required this.slug,
    required this.pricingType,
    required this.mediaFileIds,
    this.categoryId,
    this.shortDescription,
    this.description,
    this.priceAmount,
    this.provinceId,
    this.cityId,
    this.provinceName,
    this.cityName,
    this.serviceArea,
  });
  final int? categoryId;
  final String title;
  final String slug;
  final String? shortDescription;
  final String? description;
  final String pricingType;
  final double? priceAmount;
  final int? provinceId;
  final int? cityId;
  final String? provinceName;
  final String? cityName;
  final String? serviceArea;
  final List<int> mediaFileIds;
  Map<String, dynamic> toJson() => {
    'category_id': categoryId,
    'title': title,
    'slug': slug,
    'short_description': shortDescription,
    'description': description,
    'pricing_type': pricingType,
    'price_amount': priceAmount,
    'currency': 'TOMAN',
    'province_id': provinceId,
    'city_id': cityId,
    'province_name': provinceName,
    'city_name': cityName,
    'service_area': serviceArea,
    'is_active': true,
    'media_items':
        mediaFileIds
            .asMap()
            .entries
            .map(
              (entry) => {
                'media_file_id': entry.value,
                'sort_order': entry.key,
                'is_primary': entry.key == 0,
              },
            )
            .toList(),
  };
}
