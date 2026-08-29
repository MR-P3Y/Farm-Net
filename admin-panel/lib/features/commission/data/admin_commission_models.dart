class AdminCommissionSetting {
  const AdminCommissionSetting({
    required this.id,
    required this.title,
    required this.percent,
    required this.status,
    required this.isDefault,
    required this.createdAt,
    required this.updatedAt,
    this.description,
    this.createdBy,
    this.updatedBy,
  });

  final int id;
  final String title;
  final num percent;
  final String status;
  final bool isDefault;
  final String? description;
  final int? createdBy;
  final int? updatedBy;
  final String createdAt;
  final String updatedAt;

  factory AdminCommissionSetting.fromJson(Map<String, dynamic> json) {
    return AdminCommissionSetting(
      id: (json['id'] as num).toInt(),
      title: json['title']?.toString() ?? '',
      percent: _numFromJson(json['percent']),
      status: json['status']?.toString() ?? '',
      isDefault: json['is_default'] == true,
      description: json['description']?.toString(),
      createdBy:
          json['created_by'] == null
              ? null
              : (json['created_by'] as num).toInt(),
      updatedBy:
          json['updated_by'] == null
              ? null
              : (json['updated_by'] as num).toInt(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

num _numFromJson(dynamic value) {
  if (value is num) return value;
  if (value is String) return num.tryParse(value) ?? 0;
  return 0;
}

class AdminCommissionPolicy {
  const AdminCommissionPolicy({
    required this.id,
    required this.code,
    required this.title,
    required this.sourceType,
    required this.percent,
    required this.status,
    required this.isDefault,
    required this.createdAt,
    required this.updatedAt,
  });

  final int id;
  final String code;
  final String title;
  final String sourceType;
  final num percent;
  final String status;
  final bool isDefault;
  final String createdAt;
  final String updatedAt;

  factory AdminCommissionPolicy.fromJson(Map<String, dynamic> json) =>
      AdminCommissionPolicy(
        id: (json['id'] as num).toInt(),
        code: json['code']?.toString() ?? '',
        title: json['title']?.toString() ?? '',
        sourceType: json['source_type']?.toString() ?? '',
        percent: _numFromJson(json['percent']),
        status: json['status']?.toString() ?? '',
        isDefault: json['is_default'] == true,
        createdAt: json['created_at']?.toString() ?? '',
        updatedAt: json['updated_at']?.toString() ?? '',
      );
}
