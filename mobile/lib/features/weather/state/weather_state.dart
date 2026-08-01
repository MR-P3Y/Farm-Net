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
    this.selectedFarmId,
    this.selectedPlotId,
    this.selectedFarmName,
    this.selectedPlotName,
  });

  final bool isLoading;
  final bool isSaving;

  final List<WeatherLocationModel> locations;
  final WeatherLocationModel? selectedLocation;

  final WeatherSnapshotModel? current;
  final List<WeatherForecastModel> forecasts;
  final List<WeatherAlertModel> alerts;

  final String? errorMessage;
  final int? selectedFarmId;
  final int? selectedPlotId;
  final String? selectedFarmName;
  final String? selectedPlotName;

  bool get isFarmSource => selectedFarmId != null && selectedPlotId != null;
  String? get farmDisplayName {
    if (selectedFarmName == null || selectedPlotName == null) return null;
    return '$selectedFarmName · $selectedPlotName';
  }

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
    int? selectedFarmId,
    int? selectedPlotId,
    String? selectedFarmName,
    String? selectedPlotName,
    bool clearFarmSource = false,
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
      selectedFarmId:
          clearFarmSource ? null : selectedFarmId ?? this.selectedFarmId,
      selectedPlotId:
          clearFarmSource ? null : selectedPlotId ?? this.selectedPlotId,
      selectedFarmName:
          clearFarmSource ? null : selectedFarmName ?? this.selectedFarmName,
      selectedPlotName:
          clearFarmSource ? null : selectedPlotName ?? this.selectedPlotName,
    );
  }
}
