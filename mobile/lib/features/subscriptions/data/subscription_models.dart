double _number(dynamic value) =>
    value is num ? value.toDouble() : double.tryParse('$value') ?? 0;

DateTime? _date(dynamic value) =>
    value == null ? null : DateTime.tryParse(value.toString());

class SubscriptionPlanFeature {
  const SubscriptionPlanFeature({
    required this.code,
    required this.name,
    required this.module,
    required this.enabled,
    required this.unlimited,
    this.unit,
    this.value,
  });

  final String code;
  final String name;
  final String module;
  final String? unit;
  final bool enabled;
  final bool unlimited;
  final dynamic value;

  factory SubscriptionPlanFeature.fromJson(Map<String, dynamic> json) =>
      SubscriptionPlanFeature(
        code: json['code']?.toString() ?? '',
        name: json['name']?.toString() ?? '',
        module: json['module']?.toString() ?? '',
        unit: json['unit']?.toString(),
        enabled: json['enabled'] == true,
        unlimited: json['unlimited'] == true,
        value: json['value'],
      );
}

class SubscriptionPlan {
  const SubscriptionPlan({
    required this.id,
    required this.code,
    required this.name,
    required this.billingPeriod,
    required this.priceToman,
    required this.currency,
    required this.version,
    required this.isDefaultFree,
    required this.features,
    this.description,
    this.durationDays,
  });

  final int id;
  final String code;
  final String name;
  final String? description;
  final String billingPeriod;
  final int? durationDays;
  final double priceToman;
  final String currency;
  final int version;
  final bool isDefaultFree;
  final List<SubscriptionPlanFeature> features;

  bool get isFree => billingPeriod == 'free' || priceToman == 0;

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) =>
      SubscriptionPlan(
        id: (json['id'] as num?)?.toInt() ?? 0,
        code: json['code']?.toString() ?? '',
        name: json['name']?.toString() ?? '',
        description: json['description']?.toString(),
        billingPeriod: json['billing_period']?.toString() ?? '',
        durationDays: (json['duration_days'] as num?)?.toInt(),
        priceToman: _number(json['price_toman']),
        currency: json['currency']?.toString() ?? 'TOMAN',
        version: (json['version'] as num?)?.toInt() ?? 1,
        isDefaultFree: json['is_default_free'] == true,
        features:
            (json['features'] as List? ?? const [])
                .map(
                  (row) => SubscriptionPlanFeature.fromJson(
                    (row as Map).cast<String, dynamic>(),
                  ),
                )
                .toList(),
      );
}

class OwnSubscription {
  const OwnSubscription({
    required this.id,
    required this.status,
    required this.plan,
    required this.autoRenew,
    required this.cancelAtPeriodEnd,
    required this.version,
    this.startsAt,
    this.periodStartsAt,
    this.periodEndsAt,
    this.graceEndsAt,
  });

  final int id;
  final String status;
  final SubscriptionPlan plan;
  final DateTime? startsAt;
  final DateTime? periodStartsAt;
  final DateTime? periodEndsAt;
  final DateTime? graceEndsAt;
  final bool autoRenew;
  final bool cancelAtPeriodEnd;
  final int version;

  bool get isInGrace => status == 'grace';

  factory OwnSubscription.fromJson(Map<String, dynamic> json) =>
      OwnSubscription(
        id: (json['id'] as num?)?.toInt() ?? 0,
        status: json['status']?.toString() ?? '',
        plan: SubscriptionPlan.fromJson(
          (json['plan'] as Map).cast<String, dynamic>(),
        ),
        startsAt: _date(json['starts_at']),
        periodStartsAt: _date(json['current_period_starts_at']),
        periodEndsAt: _date(json['current_period_ends_at']),
        graceEndsAt: _date(json['grace_ends_at']),
        autoRenew: json['auto_renew'] == true,
        cancelAtPeriodEnd: json['cancel_at_period_end'] == true,
        version: (json['version'] as num?)?.toInt() ?? 1,
      );
}

class SubscriptionEntitlement {
  const SubscriptionEntitlement({
    required this.code,
    required this.enabled,
    required this.unlimited,
    this.limit,
  });

  final String code;
  final bool enabled;
  final bool unlimited;
  final double? limit;

  factory SubscriptionEntitlement.fromJson(Map<String, dynamic> json) =>
      SubscriptionEntitlement(
        code: json['code']?.toString() ?? '',
        enabled: json['enabled'] == true,
        unlimited: json['unlimited'] == true,
        limit:
            json['limit_value'] == null ? null : _number(json['limit_value']),
      );
}

class SubscriptionUsage {
  const SubscriptionUsage({
    required this.code,
    required this.used,
    required this.reserved,
    required this.unlimited,
    required this.periodEndsAt,
    this.limit,
    this.remaining,
  });

  final String code;
  final double used;
  final double reserved;
  final double? limit;
  final double? remaining;
  final bool unlimited;
  final DateTime periodEndsAt;

  factory SubscriptionUsage.fromJson(
    Map<String, dynamic> json,
  ) => SubscriptionUsage(
    code: json['code']?.toString() ?? '',
    used: _number(json['used_value']),
    reserved: _number(json['reserved_value']),
    limit: json['limit_value'] == null ? null : _number(json['limit_value']),
    remaining:
        json['remaining_value'] == null
            ? null
            : _number(json['remaining_value']),
    unlimited: json['unlimited'] == true,
    periodEndsAt:
        _date(json['period_ends_at']) ?? DateTime.fromMillisecondsSinceEpoch(0),
  );
}

class SubscriptionCheckout {
  const SubscriptionCheckout({
    required this.paymentAttemptId,
    required this.subscriptionId,
    required this.invoiceId,
    required this.provider,
    required this.status,
    required this.amountToman,
    required this.currency,
    required this.expiresAt,
    this.redirectUrl,
    this.verifiedAt,
  });

  final int paymentAttemptId;
  final int subscriptionId;
  final int invoiceId;
  final String provider;
  final String status;
  final double amountToman;
  final String currency;
  final String? redirectUrl;
  final DateTime expiresAt;
  final DateTime? verifiedAt;

  factory SubscriptionCheckout.fromJson(Map<String, dynamic> json) =>
      SubscriptionCheckout(
        paymentAttemptId: (json['payment_attempt_id'] as num?)?.toInt() ?? 0,
        subscriptionId: (json['subscription_id'] as num?)?.toInt() ?? 0,
        invoiceId: (json['invoice_id'] as num?)?.toInt() ?? 0,
        provider: json['provider']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
        amountToman: _number(json['amount_toman']),
        currency: json['currency']?.toString() ?? 'TOMAN',
        redirectUrl: json['redirect_url']?.toString(),
        expiresAt:
            _date(json['expires_at']) ?? DateTime.fromMillisecondsSinceEpoch(0),
        verifiedAt: _date(json['verified_at']),
      );
}
