class AdminPlanFeature {
  const AdminPlanFeature({
    required this.code,
    required this.name,
    required this.module,
    required this.valueKind,
    required this.enabled,
    required this.unlimited,
    this.unit,
    this.value,
  });

  final String code;
  final String name;
  final String module;
  final String valueKind;
  final String? unit;
  final bool enabled;
  final bool unlimited;
  final Object? value;

  factory AdminPlanFeature.fromJson(Map<String, dynamic> json) =>
      AdminPlanFeature(
        code: json['code'] as String,
        name: json['name'] as String,
        module: json['module'] as String,
        valueKind: json['value_kind'] as String,
        unit: json['unit'] as String?,
        enabled: json['enabled'] == true,
        unlimited: json['unlimited'] == true,
        value: json['value'],
      );

  Map<String, dynamic> toInput() => {
    'feature_code': code,
    'enabled': enabled,
    'unlimited': unlimited,
    if (!unlimited && valueKind == 'boolean') 'boolean_value': value == true,
    if (!unlimited && (valueKind == 'integer' || valueKind == 'decimal'))
      'numeric_value': value,
    if (!unlimited && valueKind == 'string') 'string_value': value,
    if (!unlimited && valueKind == 'json') 'json_value': value,
  };
}

class AdminBillingPlan {
  const AdminBillingPlan({
    required this.id,
    required this.code,
    required this.name,
    required this.status,
    required this.billingPeriod,
    required this.priceToman,
    required this.currency,
    required this.version,
    required this.isDefaultFree,
    required this.features,
    this.description,
    this.durationDays,
    this.effectiveFrom,
    this.effectiveUntil,
  });

  final int id;
  final String code;
  final String name;
  final String? description;
  final String status;
  final String billingPeriod;
  final int? durationDays;
  final num priceToman;
  final String currency;
  final int version;
  final bool isDefaultFree;
  final DateTime? effectiveFrom;
  final DateTime? effectiveUntil;
  final List<AdminPlanFeature> features;

  factory AdminBillingPlan.fromJson(
    Map<String, dynamic> json,
  ) => AdminBillingPlan(
    id: (json['id'] as num).toInt(),
    code: json['code'] as String,
    name: json['name'] as String,
    description: json['description'] as String?,
    status: json['status'] as String,
    billingPeriod: json['billing_period'] as String,
    durationDays: (json['duration_days'] as num?)?.toInt(),
    priceToman: num.parse(json['price_toman'].toString()),
    currency: json['currency'] as String,
    version: (json['version'] as num).toInt(),
    isDefaultFree: json['is_default_free'] == true,
    effectiveFrom: DateTime.tryParse((json['effective_from'] ?? '').toString()),
    effectiveUntil: DateTime.tryParse(
      (json['effective_until'] ?? '').toString(),
    ),
    features:
        (json['features'] as List? ?? const [])
            .map(
              (item) => AdminPlanFeature.fromJson(
                (item as Map).cast<String, dynamic>(),
              ),
            )
            .toList(),
  );
}

class AdminFeatureUsage {
  const AdminFeatureUsage({
    required this.code,
    required this.used,
    required this.reserved,
    required this.unlimited,
    this.limit,
    this.remaining,
  });

  final String code;
  final num used;
  final num reserved;
  final num? limit;
  final num? remaining;
  final bool unlimited;

  factory AdminFeatureUsage.fromJson(Map<String, dynamic> json) =>
      AdminFeatureUsage(
        code: json['code'] as String,
        used: num.parse(json['used_value'].toString()),
        reserved: num.parse(json['reserved_value'].toString()),
        limit:
            json['limit_value'] == null
                ? null
                : num.parse(json['limit_value'].toString()),
        remaining:
            json['remaining_value'] == null
                ? null
                : num.parse(json['remaining_value'].toString()),
        unlimited: json['unlimited'] == true,
      );
}

class AdminBillingSubscription {
  const AdminBillingSubscription({
    required this.id,
    required this.userId,
    required this.userLabel,
    required this.status,
    required this.planId,
    required this.planCode,
    required this.planName,
    required this.priceToman,
    required this.currency,
    required this.autoRenew,
    required this.cancelAtPeriodEnd,
    required this.activationSource,
    required this.version,
    required this.usage,
    this.startsAt,
    this.periodStartsAt,
    this.periodEndsAt,
    this.graceEndsAt,
    this.activatedByUserId,
    this.activationReason,
    this.cancellationReason,
  });

  final int id;
  final int userId;
  final String userLabel;
  final String status;
  final int planId;
  final String planCode;
  final String planName;
  final num priceToman;
  final String currency;
  final DateTime? startsAt;
  final DateTime? periodStartsAt;
  final DateTime? periodEndsAt;
  final DateTime? graceEndsAt;
  final bool autoRenew;
  final bool cancelAtPeriodEnd;
  final String activationSource;
  final int? activatedByUserId;
  final String? activationReason;
  final String? cancellationReason;
  final int version;
  final List<AdminFeatureUsage> usage;

  factory AdminBillingSubscription.fromJson(
    Map<String, dynamic> json,
  ) => AdminBillingSubscription(
    id: (json['id'] as num).toInt(),
    userId: (json['user_id'] as num).toInt(),
    userLabel: json['user_label'] as String,
    status: json['status'] as String,
    planId: (json['plan_id'] as num).toInt(),
    planCode: json['plan_code'] as String,
    planName: json['plan_name'] as String,
    priceToman: num.parse(json['price_toman'].toString()),
    currency: json['currency'] as String,
    startsAt: DateTime.tryParse((json['starts_at'] ?? '').toString()),
    periodStartsAt: DateTime.tryParse(
      (json['current_period_starts_at'] ?? '').toString(),
    ),
    periodEndsAt: DateTime.tryParse(
      (json['current_period_ends_at'] ?? '').toString(),
    ),
    graceEndsAt: DateTime.tryParse((json['grace_ends_at'] ?? '').toString()),
    autoRenew: json['auto_renew'] == true,
    cancelAtPeriodEnd: json['cancel_at_period_end'] == true,
    activationSource: json['activation_source'] as String,
    activatedByUserId: (json['activated_by_user_id'] as num?)?.toInt(),
    activationReason: json['activation_reason'] as String?,
    cancellationReason: json['cancellation_reason'] as String?,
    version: (json['version'] as num).toInt(),
    usage:
        (json['usage'] as List? ?? const [])
            .map(
              (item) => AdminFeatureUsage.fromJson(
                (item as Map).cast<String, dynamic>(),
              ),
            )
            .toList(),
  );
}

class AdminBillingPage<T> {
  const AdminBillingPage({
    required this.items,
    required this.page,
    required this.total,
    required this.totalPages,
  });

  final List<T> items;
  final int page;
  final int total;
  final int totalPages;
}
