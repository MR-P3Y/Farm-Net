import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../farms/data/farm_repository.dart';
import '../data/weather_api.dart';
import '../data/weather_models.dart';
import '../data/weather_repository.dart';
import 'weather_state.dart';

final weatherControllerProvider =
    StateNotifierProvider<WeatherController, WeatherState>((ref) {
      return WeatherController(
        repository: ref.watch(weatherRepositoryProvider),
        farmRepository: ref.watch(farmRepositoryProvider),
      );
    });

class WeatherController extends StateNotifier<WeatherState> {
  static const _sourceKindKey = 'weather_selected_source_kind';
  static const _locationIdKey = 'weather_selected_location_id';
  static const _farmIdKey = 'weather_selected_farm_id';
  static const _plotIdKey = 'weather_selected_plot_id';
  static const _farmNameKey = 'weather_selected_farm_name';
  static const _plotNameKey = 'weather_selected_plot_name';

  WeatherController({
    required WeatherRepository repository,
    required FarmRepository farmRepository,
  }) : _repository = repository,
       _farmRepository = farmRepository,
       super(WeatherState.initial());

  final WeatherRepository _repository;
  final FarmRepository _farmRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final rawLocations = await _repository.listLocations();
      final preferences = await SharedPreferences.getInstance();
      final sourceKind = preferences.getString(_sourceKindKey);
      final locations = _deduplicateLocations(
        rawLocations,
        preferredId: preferences.getInt(_locationIdKey),
      );

      if (sourceKind == 'farm') {
        final farmId = preferences.getInt(_farmIdKey);
        final plotId = preferences.getInt(_plotIdKey);
        if (farmId != null && plotId != null) {
          final farms = await _farmRepository.farms();
          final farm = farms.where((item) => item.id == farmId).firstOrNull;
          if (farm != null) {
            final plots = await _farmRepository.plots(farm.id);
            final plot = plots.where((item) => item.id == plotId).firstOrNull;
            if (plot != null &&
                plot.latitude != null &&
                plot.longitude != null) {
              state = state.copyWith(isLoading: false, locations: locations);
              await loadFarmPlot(
                farmId: farm.id,
                plotId: plot.id,
                farmName: farm.name,
                plotName: plot.name,
              );
              return;
            }
          }
        }
      }

      final storedLocationId = preferences.getInt(_locationIdKey);
      final storedLocation =
          storedLocationId == null
              ? null
              : locations
                  .where((location) => location.id == storedLocationId)
                  .firstOrNull;
      final selected = storedLocation ?? locations.firstOrNull;

      state = state.copyWith(
        isLoading: false,
        locations: locations,
        selectedLocation: selected,
      );

      if (selected != null) {
        await loadLocation(selected);
      } else {
        await _clearStoredSource();
      }
    } on WeatherApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اطلاعات آب‌وهوا',
      );
    }
  }

  Future<void> loadLocation(WeatherLocationModel location) async {
    state = state.copyWith(
      isSaving: true,
      selectedLocation: location,
      clearCurrent: true,
      clearError: true,
      clearFarmSource: true,
    );

    try {
      var current = await _repository.current(location.id);
      if (current == null) {
        await _repository.refresh(locationId: location.id);
        current = await _repository.current(location.id);
      }
      final values = await Future.wait<Object>([
        _repository.forecast(location.id),
        _repository.alerts(location.id),
      ]);

      state = state.copyWith(
        isSaving: false,
        current: current,
        forecasts: values[0] as List<WeatherForecastModel>,
        alerts: values[1] as List<WeatherAlertModel>,
      );
      await _persistLocation(location.id);
    } on WeatherApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات آب‌وهوا',
      );
    }
  }

  Future<void> refreshSelected() async {
    if (state.isFarmSource) {
      final farmId = state.selectedFarmId!;
      final plotId = state.selectedPlotId!;
      await loadFarmPlot(
        farmId: farmId,
        plotId: plotId,
        farmName: state.selectedFarmName ?? '',
        plotName: state.selectedPlotName ?? '',
        refresh: true,
      );
      return;
    }
    final location = state.selectedLocation;
    if (location == null) return;

    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.refresh(locationId: location.id);
      await loadLocation(location);
    } on WeatherApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در بروزرسانی آب‌وهوا',
      );
    }
  }

  Future<void> loadFarmPlot({
    required int farmId,
    required int plotId,
    required String farmName,
    required String plotName,
    bool refresh = false,
  }) async {
    state = state.copyWith(
      isSaving: true,
      clearCurrent: true,
      clearError: true,
      selectedFarmId: farmId,
      selectedPlotId: plotId,
      selectedFarmName: farmName,
      selectedPlotName: plotName,
    );
    try {
      final value = await _farmRepository.weather(
        farmId,
        plotId,
        refresh: refresh,
      );
      state = state.copyWith(
        isSaving: false,
        current:
            value.snapshot == null
                ? null
                : WeatherSnapshotModel.fromFarmJson(value.snapshot!),
        forecasts:
            value.forecasts.map(WeatherForecastModel.fromFarmJson).toList(),
        alerts: value.alerts.map(WeatherAlertModel.fromFarmJson).toList(),
      );
      await _persistFarm(
        farmId: farmId,
        plotId: plotId,
        farmName: farmName,
        plotName: plotName,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت آب‌وهوای قطعه مزرعه',
      );
    }
  }

  Future<void> _persistLocation(int locationId) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_sourceKindKey, 'location');
    await preferences.setInt(_locationIdKey, locationId);
    await preferences.remove(_farmIdKey);
    await preferences.remove(_plotIdKey);
    await preferences.remove(_farmNameKey);
    await preferences.remove(_plotNameKey);
  }

  Future<void> _persistFarm({
    required int farmId,
    required int plotId,
    required String farmName,
    required String plotName,
  }) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_sourceKindKey, 'farm');
    await preferences.setInt(_farmIdKey, farmId);
    await preferences.setInt(_plotIdKey, plotId);
    await preferences.setString(_farmNameKey, farmName);
    await preferences.setString(_plotNameKey, plotName);
    await preferences.remove(_locationIdKey);
  }

  Future<void> _clearStoredSource() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.remove(_sourceKindKey);
    await preferences.remove(_locationIdKey);
    await preferences.remove(_farmIdKey);
    await preferences.remove(_plotIdKey);
    await preferences.remove(_farmNameKey);
    await preferences.remove(_plotNameKey);
  }

  Future<void> createGpsLocation({
    required double latitude,
    required double longitude,
    String? displayName,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final reusable =
          state.locations
              .where((item) => item.locationType == 'gps')
              .where((item) => _isNearby(item, latitude, longitude))
              .firstOrNull;
      if (reusable != null && reusable.displayName.contains('—')) {
        await loadLocation(reusable);
        return;
      }
      final location = await _repository.createGpsLocation(
        latitude: latitude,
        longitude: longitude,
        displayName: displayName,
        timezone: 'Asia/Tehran',
      );

      final locations = _mergeLocation(state.locations, location);

      state = state.copyWith(
        isSaving: false,
        locations: locations,
        selectedLocation: location,
      );

      await _repository.refresh(locationId: location.id);
      await loadLocation(location);
    } on WeatherApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ثبت موقعیت GPS',
      );
    }
  }

  Future<void> createGeoLocation({
    required int provinceId,
    required int cityId,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final location = await _repository.createGeoLocation(
        provinceId: provinceId,
        cityId: cityId,
      );
      state = state.copyWith(
        isSaving: false,
        locations: _mergeLocation(state.locations, location),
        selectedLocation: location,
      );
      await _repository.refresh(locationId: location.id);
      await loadLocation(location);
    } on WeatherApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ثبت شهر هواشناسی',
      );
    }
  }

  static List<WeatherLocationModel> _mergeLocation(
    List<WeatherLocationModel> values,
    WeatherLocationModel location,
  ) => _deduplicateLocations([
    location,
    ...values.where((item) => item.id != location.id),
  ], preferredId: location.id);

  static List<WeatherLocationModel> _deduplicateLocations(
    List<WeatherLocationModel> values, {
    int? preferredId,
  }) {
    final result = <WeatherLocationModel>[];
    final ids = <int>{};
    final gpsValues = <WeatherLocationModel>[];
    for (final value in values) {
      if (!ids.add(value.id)) continue;
      if (value.locationType == 'gps') {
        gpsValues.add(value);
      } else {
        result.add(value);
      }
    }
    final gps =
        gpsValues.where((item) => item.id == preferredId).firstOrNull ??
        gpsValues.firstOrNull;
    if (gps != null) result.insert(0, gps);
    return result;
  }

  static bool _isNearby(
    WeatherLocationModel location,
    double latitude,
    double longitude,
  ) {
    final savedLatitude = double.tryParse(location.latitude);
    final savedLongitude = double.tryParse(location.longitude);
    if (savedLatitude == null || savedLongitude == null) return false;
    return (savedLatitude - latitude).abs() <= 0.01 &&
        (savedLongitude - longitude).abs() <= 0.01;
  }
}
