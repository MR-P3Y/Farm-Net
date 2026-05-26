import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'weather_api.dart';
import 'weather_models.dart';

final weatherRepositoryProvider = Provider<WeatherRepository>((ref) {
  return WeatherRepository(api: WeatherApi());
});

class WeatherRepository {
  WeatherRepository({required WeatherApi api}) : _api = api;

  final WeatherApi _api;

  Future<List<WeatherLocationModel>> listLocations() {
    return _api.listLocations();
  }

  Future<WeatherLocationModel> createGpsLocation({
    required double latitude,
    required double longitude,
    String? displayName,
    String? timezone,
  }) {
    return _api.createGpsLocation(
      latitude: latitude,
      longitude: longitude,
      displayName: displayName,
      timezone: timezone,
    );
  }

  Future<WeatherSnapshotModel?> current(int locationId) {
    return _api.current(locationId);
  }

  Future<List<WeatherForecastModel>> forecast(int locationId) {
    return _api.forecast(locationId);
  }

  Future<List<WeatherAlertModel>> alerts(int locationId) {
    return _api.alerts(locationId);
  }

  Future<void> refresh({required int locationId, String provider = 'mock'}) {
    return _api.refresh(locationId: locationId, provider: provider);
  }
}
