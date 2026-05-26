import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_weather_api.dart';
import '../data/admin_weather_models.dart';
import '../data/admin_weather_repository.dart';
import 'admin_weather_state.dart';

final adminWeatherControllerProvider =
    StateNotifierProvider<AdminWeatherController, AdminWeatherState>((ref) {
      return AdminWeatherController(
        repository: ref.watch(adminWeatherRepositoryProvider),
      );
    });

class AdminWeatherController extends StateNotifier<AdminWeatherState> {
  AdminWeatherController({required AdminWeatherRepository repository})
    : _repository = repository,
      super(AdminWeatherState.initial());

  final AdminWeatherRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final configs = await _repository.listProviderConfigs();
      final locations = await _repository.listLocations();
      final rules = await _repository.listAlertRules();

      final selected = locations.isEmpty ? null : locations.first;
      AdminWeatherCacheStatus? cacheStatus;
      List<AdminWeatherAlert> alerts = const [];

      if (selected != null) {
        cacheStatus = await _repository.cacheStatus(selected.id);
        alerts = await _repository.listAlerts(locationId: selected.id);
      }

      state = state.copyWith(
        isLoading: false,
        providerConfigs: configs,
        locations: locations,
        selectedLocation: selected,
        cacheStatus: cacheStatus,
        alertRules: rules,
        alerts: alerts,
      );
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اطلاعات آب‌وهوا',
      );
    }
  }

  Future<void> selectLocation(AdminWeatherLocation location) async {
    state = state.copyWith(
      isSaving: true,
      selectedLocation: location,
      clearError: true,
    );

    try {
      final cache = await _repository.cacheStatus(location.id);
      final alerts = await _repository.listAlerts(locationId: location.id);

      state = state.copyWith(
        isSaving: false,
        cacheStatus: cache,
        alerts: alerts,
      );
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت وضعیت موقعیت',
      );
    }
  }

  Future<void> refreshSelected({bool force = true}) async {
    final location = state.selectedLocation;
    if (location == null) return;

    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.refresh(locationId: location.id, force: force);
      final cache = await _repository.cacheStatus(location.id);
      final alerts = await _repository.listAlerts(locationId: location.id);

      state = state.copyWith(
        isSaving: false,
        cacheStatus: cache,
        alerts: alerts,
      );
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در بروزرسانی آب‌وهوا',
      );
    }
  }

  Future<void> seedAlertRules() async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final rules = await _repository.seedAlertRules();
      state = state.copyWith(isSaving: false, alertRules: rules);
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ساخت قوانین هشدار',
      );
    }
  }

  Future<void> evaluateSelectedAlerts() async {
    final location = state.selectedLocation;
    if (location == null) return;

    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final result = await _repository.evaluateAlerts(locationId: location.id);
      final alerts = await _repository.listAlerts(locationId: location.id);

      state = state.copyWith(
        isSaving: false,
        lastEvaluation: result,
        alerts: alerts,
      );
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ارزیابی هشدارها',
      );
    }
  }

  Future<void> updateProviderConfig(AdminWeatherProviderConfig config) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.updateProviderConfig(
        id: config.id,
        isActive: config.isActive,
        priority: config.priority,
        baseUrl: config.baseUrl,
        apiKeyRef: config.apiKeyRef,
      );

      final configs = await _repository.listProviderConfigs();

      state = state.copyWith(isSaving: false, providerConfigs: configs);
    } on AdminWeatherApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در بروزرسانی provider',
      );
    }
  }
}
