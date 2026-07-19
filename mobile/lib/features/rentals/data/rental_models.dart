class RentalCategory {
  const RentalCategory({
    required this.id,
    required this.code,
    required this.title,
  });
  final int id;
  final String code;
  final String title;

  factory RentalCategory.fromJson(Map<String, dynamic> json) => RentalCategory(
    id: (json['id'] as num?)?.toInt() ?? 0,
    code: json['code']?.toString() ?? '',
    title: json['title']?.toString() ?? '',
  );
}

class RentalMedia {
  const RentalMedia({
    required this.id,
    this.mediaFileId,
    this.publicUrl,
    this.altText,
    this.isPrimary = false,
  });
  final int id;
  final int? mediaFileId;
  final String? publicUrl;
  final String? altText;
  final bool isPrimary;

  factory RentalMedia.fromJson(Map<String, dynamic> json) => RentalMedia(
    id: (json['id'] as num?)?.toInt() ?? 0,
    mediaFileId: (json['media_file_id'] as num?)?.toInt(),
    publicUrl: json['public_url']?.toString(),
    altText: json['alt_text']?.toString(),
    isPrimary: json['is_primary'] == true,
  );
}

class RentalEquipment {
  const RentalEquipment({
    required this.id,
    required this.lessorProfileId,
    required this.title,
    required this.operatorMode,
    required this.currency,
    this.categoryId,
    this.description,
    this.manufacturer,
    this.modelName,
    this.productionYear,
    this.provinceId,
    this.cityId,
    this.deliveryAvailable = false,
    this.deliveryTerms,
    this.securityDepositAmount,
    this.lessorDisplayName,
    this.category,
    this.media = const [],
  });
  final int id;
  final int lessorProfileId;
  final int? categoryId;
  final String title;
  final String? description;
  final String? manufacturer;
  final String? modelName;
  final int? productionYear;
  final String operatorMode;
  final int? provinceId;
  final int? cityId;
  final bool deliveryAvailable;
  final String? deliveryTerms;
  final double? securityDepositAmount;
  final String currency;
  final String? lessorDisplayName;
  final RentalCategory? category;
  final List<RentalMedia> media;

  RentalMedia? get primaryMedia {
    for (final item in media) {
      if (item.isPrimary) return item;
    }
    return media.isEmpty ? null : media.first;
  }

  factory RentalEquipment.fromJson(Map<String, dynamic> json) =>
      RentalEquipment(
        id: (json['id'] as num?)?.toInt() ?? 0,
        lessorProfileId: (json['lessor_profile_id'] as num?)?.toInt() ?? 0,
        categoryId: (json['category_id'] as num?)?.toInt(),
        title: json['title']?.toString() ?? '',
        description: json['description']?.toString(),
        manufacturer: json['manufacturer']?.toString(),
        modelName: json['model_name']?.toString(),
        productionYear: (json['production_year'] as num?)?.toInt(),
        operatorMode: json['operator_mode']?.toString() ?? 'without_operator',
        provinceId: (json['province_id'] as num?)?.toInt(),
        cityId: (json['city_id'] as num?)?.toInt(),
        deliveryAvailable: json['delivery_available'] == true,
        deliveryTerms: json['delivery_terms']?.toString(),
        securityDepositAmount: _double(json['security_deposit_amount']),
        currency: json['currency']?.toString() ?? 'TOMAN',
        lessorDisplayName: json['lessor_display_name']?.toString(),
        category:
            json['category'] is Map<String, dynamic>
                ? RentalCategory.fromJson(
                  json['category'] as Map<String, dynamic>,
                )
                : null,
        media:
            (json['media'] as List? ?? const [])
                .whereType<Map<String, dynamic>>()
                .map(RentalMedia.fromJson)
                .toList(),
      );
}

class RentalPricingRule {
  const RentalPricingRule({
    required this.id,
    required this.unit,
    required this.operatorIncluded,
    required this.priceAmount,
    required this.minimumUnits,
    required this.currency,
  });
  final int id;
  final String unit;
  final bool operatorIncluded;
  final double priceAmount;
  final double minimumUnits;
  final String currency;

  factory RentalPricingRule.fromJson(Map<String, dynamic> json) =>
      RentalPricingRule(
        id: (json['id'] as num?)?.toInt() ?? 0,
        unit: json['unit']?.toString() ?? '',
        operatorIncluded: json['operator_included'] == true,
        priceAmount: _double(json['price_amount']) ?? 0,
        minimumUnits: _double(json['minimum_units']) ?? 1,
        currency: json['currency']?.toString() ?? 'TOMAN',
      );
  Map<String, dynamic> toInputJson() => {
    'unit': unit,
    'operator_included': operatorIncluded,
    'price_amount': priceAmount,
    'minimum_units': minimumUnits,
    'currency': currency,
    'is_active': true,
  };
}

class RentalEquipmentDetail {
  const RentalEquipmentDetail({required this.equipment, required this.pricing});
  final RentalEquipment equipment;
  final List<RentalPricingRule> pricing;
}

class RentalAvailabilityCheck {
  const RentalAvailabilityCheck({required this.isAvailable});
  final bool isAvailable;
  factory RentalAvailabilityCheck.fromJson(Map<String, dynamic> json) =>
      RentalAvailabilityCheck(isAvailable: json['is_available'] == true);
}

class RentalRequestInput {
  const RentalRequestInput({
    required this.equipmentId,
    required this.pricingRuleId,
    required this.startsAt,
    required this.endsAt,
    required this.requestedUnits,
    required this.operatorRequested,
    this.deliveryAddress,
    this.requesterNote,
  });
  final int equipmentId;
  final int pricingRuleId;
  final DateTime startsAt;
  final DateTime endsAt;
  final double requestedUnits;
  final bool operatorRequested;
  final String? deliveryAddress;
  final String? requesterNote;
  Map<String, dynamic> toJson() => {
    'equipment_id': equipmentId,
    'pricing_rule_id': pricingRuleId,
    'starts_at': startsAt.toUtc().toIso8601String(),
    'ends_at': endsAt.toUtc().toIso8601String(),
    'requested_units': requestedUnits,
    'operator_requested': operatorRequested,
    if (deliveryAddress?.trim().isNotEmpty ?? false)
      'delivery_address': deliveryAddress!.trim(),
    if (requesterNote?.trim().isNotEmpty ?? false)
      'requester_note': requesterNote!.trim(),
  };
}

class RentalRequestStatusLog {
  const RentalRequestStatusLog({
    required this.id,
    required this.toStatus,
    required this.createdAt,
    this.fromStatus,
    this.note,
  });
  final int id;
  final String? fromStatus;
  final String toStatus;
  final DateTime createdAt;
  final String? note;
  factory RentalRequestStatusLog.fromJson(Map<String, dynamic> json) =>
      RentalRequestStatusLog(
        id: (json['id'] as num?)?.toInt() ?? 0,
        fromStatus: json['from_status']?.toString(),
        toStatus: json['to_status']?.toString() ?? '',
        createdAt:
            DateTime.tryParse(json['created_at']?.toString() ?? '') ??
            DateTime(1970),
        note: json['note']?.toString(),
      );
}

class RentalRequest {
  const RentalRequest({
    required this.id,
    required this.equipmentId,
    required this.pricingRuleId,
    required this.equipmentTitle,
    required this.startsAt,
    required this.endsAt,
    required this.requestedUnits,
    required this.operatorRequested,
    required this.status,
    required this.currency,
    this.lessorDisplayName,
    this.pricePerUnit,
    this.rentalAmount,
    this.depositAmount,
    this.totalAmount,
    this.deliveryAddress,
    this.requesterNote,
    this.lessorNote,
    this.cancelReason,
    this.statusLogs = const [],
  });
  final int id;
  final int equipmentId;
  final int pricingRuleId;
  final String equipmentTitle;
  final String? lessorDisplayName;
  final DateTime startsAt;
  final DateTime endsAt;
  final double requestedUnits;
  final bool operatorRequested;
  final String status;
  final double? pricePerUnit;
  final double? rentalAmount;
  final double? depositAmount;
  final double? totalAmount;
  final String currency;
  final String? deliveryAddress;
  final String? requesterNote;
  final String? lessorNote;
  final String? cancelReason;
  final List<RentalRequestStatusLog> statusLogs;
  bool get canCancel => status == 'pending' || status == 'accepted';
  List<String> get lessorNextStatuses => switch (status) {
    'pending' => const ['accepted', 'rejected'],
    'accepted' => const ['in_progress'],
    'in_progress' => const ['completed'],
    _ => const [],
  };
  factory RentalRequest.fromJson(Map<String, dynamic> json) => RentalRequest(
    id: (json['id'] as num?)?.toInt() ?? 0,
    equipmentId: (json['equipment_id'] as num?)?.toInt() ?? 0,
    pricingRuleId: (json['pricing_rule_id'] as num?)?.toInt() ?? 0,
    equipmentTitle: json['equipment_title']?.toString() ?? '',
    lessorDisplayName: json['lessor_display_name']?.toString(),
    startsAt:
        DateTime.tryParse(json['starts_at']?.toString() ?? '') ??
        DateTime(1970),
    endsAt:
        DateTime.tryParse(json['ends_at']?.toString() ?? '') ?? DateTime(1970),
    requestedUnits: _double(json['requested_units']) ?? 0,
    operatorRequested: json['operator_requested'] == true,
    status: json['status']?.toString() ?? 'pending',
    pricePerUnit: _double(json['price_per_unit_snapshot']),
    rentalAmount: _double(json['rental_amount_snapshot']),
    depositAmount: _double(json['deposit_amount_snapshot']),
    totalAmount: _double(json['total_amount_snapshot']),
    currency: json['currency']?.toString() ?? 'TOMAN',
    deliveryAddress: json['delivery_address']?.toString(),
    requesterNote: json['requester_note']?.toString(),
    lessorNote: json['lessor_note']?.toString(),
    cancelReason: json['cancel_reason']?.toString(),
    statusLogs:
        (json['status_logs'] as List? ?? const [])
            .whereType<Map<String, dynamic>>()
            .map(RentalRequestStatusLog.fromJson)
            .toList(),
  );
}

class LessorProfile {
  const LessorProfile({
    required this.id,
    required this.status,
    this.displayName,
    this.bio,
    this.phone,
    this.provinceId,
    this.cityId,
    this.addressText,
    this.avatarMediaFileId,
    this.adminNote,
    this.equipmentCount = 0,
  });
  final int id;
  final String status;
  final String? displayName;
  final String? bio;
  final String? phone;
  final int? provinceId;
  final int? cityId;
  final String? addressText;
  final int? avatarMediaFileId;
  final String? adminNote;
  final int equipmentCount;
  bool get canEdit => status == 'draft' || status == 'rejected';
  bool get canSubmit => canEdit;
  factory LessorProfile.fromJson(Map<String, dynamic> json) => LessorProfile(
    id: (json['id'] as num?)?.toInt() ?? 0,
    status: json['status']?.toString() ?? 'draft',
    displayName: json['display_name']?.toString(),
    bio: json['bio']?.toString(),
    phone: json['phone']?.toString(),
    provinceId: (json['province_id'] as num?)?.toInt(),
    cityId: (json['city_id'] as num?)?.toInt(),
    addressText: json['address_text']?.toString(),
    avatarMediaFileId: (json['avatar_media_file_id'] as num?)?.toInt(),
    adminNote: json['admin_note']?.toString(),
    equipmentCount: (json['equipment_count'] as num?)?.toInt() ?? 0,
  );
}

class LessorProfileInput {
  const LessorProfileInput({
    this.displayName,
    this.bio,
    this.phone,
    this.provinceId,
    this.cityId,
    this.addressText,
    this.avatarMediaFileId,
  });
  final String? displayName;
  final String? bio;
  final String? phone;
  final int? provinceId;
  final int? cityId;
  final String? addressText;
  final int? avatarMediaFileId;
  Map<String, dynamic> toJson() => {
    'display_name': displayName,
    'bio': bio,
    'phone': phone,
    'province_id': provinceId,
    'city_id': cityId,
    'address_text': addressText,
    'avatar_media_file_id': avatarMediaFileId,
  };
}

class RentalEquipmentOwner extends RentalEquipment {
  const RentalEquipmentOwner({
    required super.id,
    required super.lessorProfileId,
    required super.title,
    required super.operatorMode,
    required super.currency,
    required this.slug,
    required this.status,
    super.categoryId,
    super.description,
    super.manufacturer,
    super.modelName,
    super.productionYear,
    super.provinceId,
    super.cityId,
    super.deliveryAvailable,
    super.deliveryTerms,
    super.securityDepositAmount,
    super.lessorDisplayName,
    super.category,
    super.media,
    this.addressText,
    this.adminNote,
  });
  final String slug;
  final String status;
  final String? addressText;
  final String? adminNote;
  bool get canEdit => status == 'draft' || status == 'rejected';
  bool get canSubmit => canEdit;
  factory RentalEquipmentOwner.fromJson(Map<String, dynamic> json) {
    final base = RentalEquipment.fromJson(json);
    return RentalEquipmentOwner(
      id: base.id,
      lessorProfileId: base.lessorProfileId,
      title: base.title,
      operatorMode: base.operatorMode,
      currency: base.currency,
      slug: json['slug']?.toString() ?? '',
      status: json['status']?.toString() ?? 'draft',
      categoryId: base.categoryId,
      description: base.description,
      manufacturer: base.manufacturer,
      modelName: base.modelName,
      productionYear: base.productionYear,
      provinceId: base.provinceId,
      cityId: base.cityId,
      deliveryAvailable: base.deliveryAvailable,
      deliveryTerms: base.deliveryTerms,
      securityDepositAmount: base.securityDepositAmount,
      lessorDisplayName: base.lessorDisplayName,
      category: base.category,
      media: base.media,
      addressText: json['address_text']?.toString(),
      adminNote: json['admin_note']?.toString(),
    );
  }
}

class RentalEquipmentInput {
  const RentalEquipmentInput({
    required this.title,
    required this.slug,
    required this.operatorMode,
    required this.mediaFileIds,
    this.categoryId,
    this.description,
    this.manufacturer,
    this.modelName,
    this.productionYear,
    this.provinceId,
    this.cityId,
    this.addressText,
    this.deliveryAvailable = false,
    this.deliveryTerms,
    this.securityDepositAmount,
  });
  final String title;
  final String slug;
  final String operatorMode;
  final List<int> mediaFileIds;
  final int? categoryId;
  final String? description;
  final String? manufacturer;
  final String? modelName;
  final int? productionYear;
  final int? provinceId;
  final int? cityId;
  final String? addressText;
  final bool deliveryAvailable;
  final String? deliveryTerms;
  final double? securityDepositAmount;
  Map<String, dynamic> toJson() => {
    'category_id': categoryId,
    'title': title,
    'slug': slug,
    'description': description,
    'manufacturer': manufacturer,
    'model_name': modelName,
    'production_year': productionYear,
    'operator_mode': operatorMode,
    'province_id': provinceId,
    'city_id': cityId,
    'address_text': addressText,
    'delivery_available': deliveryAvailable,
    'delivery_terms': deliveryTerms,
    'security_deposit_amount': securityDepositAmount,
    'currency': 'TOMAN',
    'is_active': true,
    'media_items':
        mediaFileIds
            .asMap()
            .entries
            .map(
              (e) => {
                'media_file_id': e.value,
                'sort_order': e.key,
                'is_primary': e.key == 0,
              },
            )
            .toList(),
  };
}

class RentalAvailabilityBlock {
  const RentalAvailabilityBlock({
    required this.id,
    required this.equipmentId,
    required this.blockType,
    required this.startsAt,
    required this.endsAt,
    this.note,
  });
  final int id;
  final int equipmentId;
  final String blockType;
  final DateTime startsAt;
  final DateTime endsAt;
  final String? note;
  factory RentalAvailabilityBlock.fromJson(Map<String, dynamic> json) =>
      RentalAvailabilityBlock(
        id: (json['id'] as num?)?.toInt() ?? 0,
        equipmentId: (json['equipment_id'] as num?)?.toInt() ?? 0,
        blockType: json['block_type']?.toString() ?? '',
        startsAt: DateTime.parse(json['starts_at'].toString()),
        endsAt: DateTime.parse(json['ends_at'].toString()),
        note: json['note']?.toString(),
      );
  Map<String, dynamic> toJson() => {
    'block_type': blockType,
    'starts_at': startsAt.toUtc().toIso8601String(),
    'ends_at': endsAt.toUtc().toIso8601String(),
    'note': note,
  };
}

double? _double(Object? value) =>
    value is num ? value.toDouble() : double.tryParse(value?.toString() ?? '');

String rentalOperatorLabel(String value) =>
    const {
      'with_operator': 'همراه اپراتور',
      'without_operator': 'بدون اپراتور',
      'either': 'با یا بدون اپراتور',
    }[value] ??
    value;

String rentalUnitLabel(String value) =>
    const {
      'hour': 'ساعت',
      'day': 'روز',
      'week': 'هفته',
      'hectare': 'هکتار',
      'project': 'پروژه',
    }[value] ??
    value;

String rentalRequestStatusLabel(String value) =>
    const {
      'pending': 'در انتظار پاسخ',
      'accepted': 'پذیرفته‌شده',
      'rejected': 'ردشده',
      'in_progress': 'در حال اجاره',
      'completed': 'تکمیل‌شده',
      'cancelled': 'لغوشده',
    }[value] ??
    value;
