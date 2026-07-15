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
