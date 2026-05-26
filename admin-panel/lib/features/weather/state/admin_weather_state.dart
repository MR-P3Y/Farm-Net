import '../data/admin_weather_models.dart';

class AdminWeatherState {
  const AdminWeatherState({
    required this.isLoading,
    this.isSaving = false,
    this.providerConfigs = const [],
    this.locations = const [],
    this.selectedLocation,
    this.cacheStatus,
    this.alertRules = const [],
    this.alerts = const [],
    this.lastEvaluation,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;

  final List<AdminWeatherProviderConfig> providerConfigs;
  final List<AdminWeatherLocation> locations;
  final AdminWeatherLocation? selectedLocation;
  final AdminWeatherCacheStatus? cacheStatus;

  final List<AdminWeatherAlertRule> alertRules;
  final List<AdminWeatherAlert> alerts;
  final AdminWeatherAlertEvaluation? lastEvaluation;

  final String? errorMessage;

  factory AdminWeatherState.initial() {
    return const AdminWeatherState(isLoading: true);
  }

  AdminWeatherState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminWeatherProviderConfig>? providerConfigs,
    List<AdminWeatherLocation>? locations,
    AdminWeatherLocation? selectedLocation,
    AdminWeatherCacheStatus? cacheStatus,
    List<AdminWeatherAlertRule>? alertRules,
    List<AdminWeatherAlert>? alerts,
    AdminWeatherAlertEvaluation? lastEvaluation,
    String? errorMessage,
    bool clearError = false,
  }) {
    return AdminWeatherState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      providerConfigs: providerConfigs ?? this.providerConfigs,
      locations: locations ?? this.locations,
      selectedLocation: selectedLocation ?? this.selectedLocation,
      cacheStatus: cacheStatus ?? this.cacheStatus,
      alertRules: alertRules ?? this.alertRules,
      alerts: alerts ?? this.alerts,
      lastEvaluation: lastEvaluation ?? this.lastEvaluation,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
