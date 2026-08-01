class WeatherLocationModel {
  const WeatherLocationModel({
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
    this.timezone,
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
  final String? timezone;

  factory WeatherLocationModel.fromJson(Map<String, dynamic> json) {
    return WeatherLocationModel(
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
      timezone: json['timezone']?.toString(),
    );
  }
}

class WeatherSnapshotModel {
  const WeatherSnapshotModel({
    required this.id,
    required this.locationId,
    required this.provider,
    required this.observedAt,
    this.temperatureC,
    this.feelsLikeC,
    this.humidityPercent,
    this.windSpeedMps,
    this.windDirectionDeg,
    this.pressureHpa,
    this.conditionCode,
    this.conditionText,
  });

  final int id;
  final int locationId;
  final String provider;
  final String observedAt;

  final String? temperatureC;
  final String? feelsLikeC;
  final String? humidityPercent;
  final String? windSpeedMps;
  final int? windDirectionDeg;
  final String? pressureHpa;
  final String? conditionCode;
  final String? conditionText;

  factory WeatherSnapshotModel.fromJson(Map<String, dynamic> json) {
    return WeatherSnapshotModel(
      id: (json['id'] as num).toInt(),
      locationId: (json['location_id'] as num).toInt(),
      provider: json['provider']?.toString() ?? '',
      temperatureC: json['temperature_c']?.toString(),
      feelsLikeC: json['feels_like_c']?.toString(),
      humidityPercent: json['humidity_percent']?.toString(),
      windSpeedMps: json['wind_speed_mps']?.toString(),
      windDirectionDeg:
          json['wind_direction_deg'] == null
              ? null
              : (json['wind_direction_deg'] as num).toInt(),
      pressureHpa: json['pressure_hpa']?.toString(),
      conditionCode: json['condition_code']?.toString(),
      conditionText: json['condition_text']?.toString(),
      observedAt: json['observed_at']?.toString() ?? '',
    );
  }

  factory WeatherSnapshotModel.fromFarmJson(Map<String, dynamic> json) {
    return WeatherSnapshotModel(
      id: 0,
      locationId: 0,
      provider: json['provider']?.toString() ?? '',
      temperatureC: json['temperature_c']?.toString(),
      feelsLikeC: json['feels_like_c']?.toString(),
      humidityPercent: json['humidity_percent']?.toString(),
      windSpeedMps: json['wind_speed_mps']?.toString(),
      windDirectionDeg:
          json['wind_direction_deg'] == null
              ? null
              : (json['wind_direction_deg'] as num).toInt(),
      pressureHpa: json['pressure_hpa']?.toString(),
      conditionCode: json['condition_code']?.toString(),
      conditionText: json['condition_text']?.toString(),
      observedAt: json['observed_at']?.toString() ?? '',
    );
  }
}

class WeatherForecastModel {
  const WeatherForecastModel({
    required this.id,
    required this.locationId,
    required this.provider,
    required this.forecastType,
    required this.forecastTime,
    this.temperatureC,
    this.minTemperatureC,
    this.maxTemperatureC,
    this.humidityPercent,
    this.precipitationMm,
    this.precipitationProbability,
    this.windSpeedMps,
    this.conditionText,
  });

  final int id;
  final int locationId;
  final String provider;
  final String forecastType;
  final String forecastTime;

  final String? temperatureC;
  final String? minTemperatureC;
  final String? maxTemperatureC;
  final String? humidityPercent;
  final String? precipitationMm;
  final String? precipitationProbability;
  final String? windSpeedMps;
  final String? conditionText;

  factory WeatherForecastModel.fromJson(Map<String, dynamic> json) {
    return WeatherForecastModel(
      id: (json['id'] as num).toInt(),
      locationId: (json['location_id'] as num).toInt(),
      provider: json['provider']?.toString() ?? '',
      forecastType: json['forecast_type']?.toString() ?? '',
      forecastTime: json['forecast_time']?.toString() ?? '',
      temperatureC: json['temperature_c']?.toString(),
      minTemperatureC: json['min_temperature_c']?.toString(),
      maxTemperatureC: json['max_temperature_c']?.toString(),
      humidityPercent: json['humidity_percent']?.toString(),
      precipitationMm: json['precipitation_mm']?.toString(),
      precipitationProbability: json['precipitation_probability']?.toString(),
      windSpeedMps: json['wind_speed_mps']?.toString(),
      conditionText: json['condition_text']?.toString(),
    );
  }

  factory WeatherForecastModel.fromFarmJson(Map<String, dynamic> json) {
    return WeatherForecastModel(
      id: 0,
      locationId: 0,
      provider: json['provider']?.toString() ?? '',
      forecastType: json['forecast_type']?.toString() ?? '',
      forecastTime: json['forecast_time']?.toString() ?? '',
      temperatureC: json['temperature_c']?.toString(),
      minTemperatureC: json['min_temperature_c']?.toString(),
      maxTemperatureC: json['max_temperature_c']?.toString(),
      humidityPercent: json['humidity_percent']?.toString(),
      precipitationMm: json['precipitation_mm']?.toString(),
      precipitationProbability: json['precipitation_probability']?.toString(),
      windSpeedMps: json['wind_speed_mps']?.toString(),
      conditionText: json['condition_text']?.toString(),
    );
  }
}

class WeatherAlertModel {
  const WeatherAlertModel({
    required this.id,
    required this.locationId,
    required this.alertType,
    required this.severity,
    required this.status,
    required this.title,
    required this.body,
    required this.startsAt,
    required this.isActive,
    this.ruleId,
    this.endsAt,
    this.payload = const {},
    this.createdAt,
    this.updatedAt,
  });

  final int id;
  final int locationId;
  final String alertType;
  final String severity;
  final String status;
  final String title;
  final String body;
  final String startsAt;
  final int? ruleId;
  final String? endsAt;
  final bool isActive;
  final Map<String, dynamic> payload;
  final String? createdAt;
  final String? updatedAt;

  bool get isCritical => severity == 'critical';
  bool get isHighPriority => severity == 'high' || isCritical;

  factory WeatherAlertModel.fromJson(Map<String, dynamic> json) {
    return WeatherAlertModel(
      id: (json['id'] as num).toInt(),
      locationId: (json['location_id'] as num).toInt(),
      alertType: json['alert_type']?.toString() ?? '',
      severity: json['severity']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      body: json['body']?.toString() ?? '',
      startsAt: json['starts_at']?.toString() ?? '',
      ruleId: json['rule_id'] == null ? null : (json['rule_id'] as num).toInt(),
      endsAt: json['ends_at']?.toString(),
      isActive: json['is_active'] == true,
      payload:
          json['payload_json'] is Map
              ? Map<String, dynamic>.from(json['payload_json'] as Map)
              : const {},
      createdAt: json['created_at']?.toString(),
      updatedAt: json['updated_at']?.toString(),
    );
  }

  factory WeatherAlertModel.fromFarmJson(Map<String, dynamic> json) {
    return WeatherAlertModel(
      id: (json['id'] as num).toInt(),
      locationId: 0,
      alertType: json['alert_type']?.toString() ?? '',
      severity: json['severity']?.toString() ?? '',
      status: 'active',
      title: json['title']?.toString() ?? '',
      body: json['body']?.toString() ?? '',
      startsAt: json['starts_at']?.toString() ?? '',
      endsAt: json['ends_at']?.toString(),
      isActive: true,
    );
  }
}
