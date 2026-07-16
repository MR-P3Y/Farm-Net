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
    this.publicUrl,
    this.filePath,
    this.altText,
    this.isPrimary = false,
  });

  final int id;
  final String? publicUrl;
  final String? filePath;
  final String? altText;
  final bool isPrimary;

  String? get displayUrl => publicUrl ?? filePath;

  factory ServiceMedia.fromJson(Map<String, dynamic> json) => ServiceMedia(
    id: (json['id'] as num?)?.toInt() ?? 0,
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
