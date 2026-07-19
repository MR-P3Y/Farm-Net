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
    this.publicUrl,
    this.altText,
    this.isPrimary = false,
  });
  final int id;
  final String? publicUrl;
  final String? altText;
  final bool isPrimary;

  factory RentalMedia.fromJson(Map<String, dynamic> json) => RentalMedia(
    id: (json['id'] as num?)?.toInt() ?? 0,
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
