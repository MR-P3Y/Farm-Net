class AdminWeatherProviderConfig {
  const AdminWeatherProviderConfig({
    required this.id,
    required this.provider,
    required this.isActive,
    required this.priority,
    this.baseUrl,
    this.apiKeyRef,
    this.settingsJson,
  });

  final int id;
  final String provider;
  final String? baseUrl;
  final String? apiKeyRef;
  final bool isActive;
  final int priority;
  final Map<String, dynamic>? settingsJson;

  factory AdminWeatherProviderConfig.fromJson(Map<String, dynamic> json) {
    return AdminWeatherProviderConfig(
      id: (json['id'] as num).toInt(),
      provider: json['provider']?.toString() ?? '',
      baseUrl: json['base_url']?.toString(),
      apiKeyRef: json['api_key_ref']?.toString(),
      isActive: json['is_active'] == true,
      priority: (json['priority'] as num?)?.toInt() ?? 100,
      settingsJson:
          json['settings_json'] is Map<String, dynamic>
              ? json['settings_json'] as Map<String, dynamic>
              : null,
    );
  }
}

class AdminWeatherLocation {
  const AdminWeatherLocation({
    required this.id,
    required this.displayName,
    required this.locationType,
    required this.latitude,
    required this.longitude,
    required this.isActive,
    this.countryCode,
    this.provinceName,
    this.cityName,
    this.villageName,
  });

  final int id;
  final String displayName;
  final String locationType;
  final String latitude;
  final String longitude;
  final bool isActive;

  final String? countryCode;
  final String? provinceName;
  final String? cityName;
  final String? villageName;

  factory AdminWeatherLocation.fromJson(Map<String, dynamic> json) {
    return AdminWeatherLocation(
      id: (json['id'] as num).toInt(),
      displayName: json['display_name']?.toString() ?? '',
      locationType: json['location_type']?.toString() ?? '',
      latitude: json['latitude']?.toString() ?? '',
      longitude: json['longitude']?.toString() ?? '',
      isActive: json['is_active'] == true,
      countryCode: json['country_code']?.toString(),
      provinceName: json['province_name']?.toString(),
      cityName: json['city_name']?.toString(),
      villageName: json['village_name']?.toString(),
    );
  }
}

class AdminWeatherCacheStatus {
  const AdminWeatherCacheStatus({
    required this.locationId,
    required this.currentStale,
    required this.forecastStale,
    required this.weatherStale,
    required this.currentTtlMinutes,
    required this.forecastTtlMinutes,
  });

  final int locationId;
  final bool currentStale;
  final bool forecastStale;
  final bool weatherStale;
  final int currentTtlMinutes;
  final int forecastTtlMinutes;

  factory AdminWeatherCacheStatus.fromJson(Map<String, dynamic> json) {
    return AdminWeatherCacheStatus(
      locationId: (json['location_id'] as num).toInt(),
      currentStale: json['current_stale'] == true,
      forecastStale: json['forecast_stale'] == true,
      weatherStale: json['weather_stale'] == true,
      currentTtlMinutes: (json['current_ttl_minutes'] as num?)?.toInt() ?? 0,
      forecastTtlMinutes: (json['forecast_ttl_minutes'] as num?)?.toInt() ?? 0,
    );
  }
}

class AdminWeatherAlertRule {
  const AdminWeatherAlertRule({
    required this.id,
    required this.alertType,
    required this.severity,
    required this.titleTemplate,
    required this.bodyTemplate,
    required this.isActive,
  });

  final int id;
  final String alertType;
  final String severity;
  final String titleTemplate;
  final String bodyTemplate;
  final bool isActive;

  factory AdminWeatherAlertRule.fromJson(Map<String, dynamic> json) {
    return AdminWeatherAlertRule(
      id: (json['id'] as num).toInt(),
      alertType: json['alert_type']?.toString() ?? '',
      severity: json['severity']?.toString() ?? '',
      titleTemplate: json['title_template']?.toString() ?? '',
      bodyTemplate: json['body_template']?.toString() ?? '',
      isActive: json['is_active'] == true,
    );
  }
}

class AdminWeatherAlert {
  const AdminWeatherAlert({
    required this.id,
    required this.locationId,
    required this.alertType,
    required this.severity,
    required this.status,
    required this.title,
    required this.body,
    required this.startsAt,
    required this.isActive,
  });

  final int id;
  final int locationId;
  final String alertType;
  final String severity;
  final String status;
  final String title;
  final String body;
  final String startsAt;
  final bool isActive;

  factory AdminWeatherAlert.fromJson(Map<String, dynamic> json) {
    return AdminWeatherAlert(
      id: (json['id'] as num).toInt(),
      locationId: (json['location_id'] as num).toInt(),
      alertType: json['alert_type']?.toString() ?? '',
      severity: json['severity']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      body: json['body']?.toString() ?? '',
      startsAt: json['starts_at']?.toString() ?? '',
      isActive: json['is_active'] == true,
    );
  }
}

class AdminWeatherAlertEvaluation {
  const AdminWeatherAlertEvaluation({
    required this.locationId,
    required this.evaluatedRules,
    required this.createdAlerts,
    required this.skippedDuplicates,
  });

  final int locationId;
  final int evaluatedRules;
  final int createdAlerts;
  final int skippedDuplicates;

  factory AdminWeatherAlertEvaluation.fromJson(Map<String, dynamic> json) {
    return AdminWeatherAlertEvaluation(
      locationId: (json['location_id'] as num).toInt(),
      evaluatedRules: (json['evaluated_rules'] as num?)?.toInt() ?? 0,
      createdAlerts: (json['created_alerts'] as num?)?.toInt() ?? 0,
      skippedDuplicates: (json['skipped_duplicates'] as num?)?.toInt() ?? 0,
    );
  }
}
