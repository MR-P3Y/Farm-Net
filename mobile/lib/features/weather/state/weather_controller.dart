import 'package:flutter_riverpod/flutter_riverpod.dart';

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
      final locations = await _repository.listLocations();
      final selected = locations.isEmpty ? null : locations.first;

      state = state.copyWith(
        isLoading: false,
        locations: locations,
        selectedLocation: selected,
      );

      if (selected != null) {
        await loadLocation(selected);
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
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت آب‌وهوای قطعه مزرعه',
      );
    }
  }

  Future<void> createGpsLocation({
    required double latitude,
    required double longitude,
    String? displayName,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final location = await _repository.createGpsLocation(
        latitude: latitude,
        longitude: longitude,
        displayName: displayName,
        timezone: 'Asia/Tehran',
      );

      final locations = [location, ...state.locations];

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
        locations: [location, ...state.locations],
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
}
