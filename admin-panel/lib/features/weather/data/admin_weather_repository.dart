import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_weather_api.dart';
import 'admin_weather_models.dart';

final adminWeatherRepositoryProvider = Provider<AdminWeatherRepository>((ref) {
  return AdminWeatherRepository(api: AdminWeatherApi());
});

class AdminWeatherRepository {
  AdminWeatherRepository({required AdminWeatherApi api}) : _api = api;

  final AdminWeatherApi _api;

  Future<List<AdminWeatherProviderConfig>> listProviderConfigs() {
    return _api.listProviderConfigs();
  }

  Future<AdminWeatherProviderConfig> updateProviderConfig({
    required int id,
    required bool isActive,
    required int priority,
    String? baseUrl,
    String? apiKeyRef,
  }) {
    return _api.updateProviderConfig(
      id: id,
      isActive: isActive,
      priority: priority,
      baseUrl: baseUrl,
      apiKeyRef: apiKeyRef,
    );
  }

  Future<List<AdminWeatherLocation>> listLocations() {
    return _api.listLocations();
  }

  Future<AdminWeatherCacheStatus> cacheStatus(int locationId) {
    return _api.cacheStatus(locationId);
  }

  Future<void> refresh({
    required int locationId,
    String provider = 'mock',
    bool force = true,
  }) {
    return _api.refresh(
      locationId: locationId,
      provider: provider,
      force: force,
    );
  }

  Future<List<AdminWeatherAlertRule>> listAlertRules() {
    return _api.listAlertRules();
  }

  Future<List<AdminWeatherAlertRule>> seedAlertRules() {
    return _api.seedAlertRules();
  }

  Future<List<AdminWeatherAlert>> listAlerts({int? locationId}) {
    return _api.listAlerts(locationId: locationId);
  }

  Future<AdminWeatherAlertEvaluation> evaluateAlerts({
    required int locationId,
  }) {
    return _api.evaluateAlerts(locationId: locationId);
  }
}
