import '../data/weather_models.dart';

class WeatherState {
  const WeatherState({
    required this.isLoading,
    this.isSaving = false,
    this.locations = const [],
    this.selectedLocation,
    this.current,
    this.forecasts = const [],
    this.alerts = const [],
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;

  final List<WeatherLocationModel> locations;
  final WeatherLocationModel? selectedLocation;

  final WeatherSnapshotModel? current;
  final List<WeatherForecastModel> forecasts;
  final List<WeatherAlertModel> alerts;

  final String? errorMessage;

  factory WeatherState.initial() {
    return const WeatherState(isLoading: true);
  }

  WeatherState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<WeatherLocationModel>? locations,
    WeatherLocationModel? selectedLocation,
    WeatherSnapshotModel? current,
    List<WeatherForecastModel>? forecasts,
    List<WeatherAlertModel>? alerts,
    String? errorMessage,
    bool clearCurrent = false,
    bool clearError = false,
  }) {
    return WeatherState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      locations: locations ?? this.locations,
      selectedLocation: selectedLocation ?? this.selectedLocation,
      current: clearCurrent ? null : current ?? this.current,
      forecasts: forecasts ?? this.forecasts,
      alerts: alerts ?? this.alerts,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
