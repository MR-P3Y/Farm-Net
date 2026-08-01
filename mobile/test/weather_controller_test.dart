import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/farms/data/farm_repository.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:farm_net/features/weather/data/weather_repository.dart';
import 'package:farm_net/features/weather/state/weather_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  const deland = WeatherLocationModel(
    id: 1,
    displayName: 'Deland',
    locationType: 'city',
    latitude: '36.8',
    longitude: '54.0',
    isActive: true,
  );
  const tehran = WeatherLocationModel(
    id: 2,
    displayName: 'Tehran',
    locationType: 'city',
    latitude: '35.7',
    longitude: '51.4',
    isActive: true,
  );

  test('load restores the last selected public weather location', () async {
    SharedPreferences.setMockInitialValues({
      'weather_selected_source_kind': 'location',
      'weather_selected_location_id': 2,
    });
    final controller = WeatherController(
      repository: _WeatherRepository([deland, tehran]),
      farmRepository: _FarmRepository(),
    );

    await controller.load();

    expect(controller.state.selectedLocation?.id, 2);
    expect(controller.state.selectedLocation?.displayName, 'Tehran');
    expect(controller.state.isFarmSource, isFalse);
  });

  test('load restores the last selected private farm plot source', () async {
    SharedPreferences.setMockInitialValues({
      'weather_selected_source_kind': 'farm',
      'weather_selected_farm_id': 10,
      'weather_selected_plot_id': 20,
    });
    final controller = WeatherController(
      repository: _WeatherRepository([deland]),
      farmRepository: _FarmRepository(),
    );

    await controller.load();

    expect(controller.state.isFarmSource, isTrue);
    expect(controller.state.selectedFarmId, 10);
    expect(controller.state.selectedPlotId, 20);
    expect(controller.state.farmDisplayName, 'My farm · North plot');
    expect(controller.state.current?.temperatureC, '24.5');
  });

  test('selecting a location replaces a stored farm source', () async {
    SharedPreferences.setMockInitialValues({
      'weather_selected_source_kind': 'farm',
      'weather_selected_farm_id': 10,
      'weather_selected_plot_id': 20,
    });
    final controller = WeatherController(
      repository: _WeatherRepository([deland, tehran]),
      farmRepository: _FarmRepository(),
    );

    await controller.loadLocation(tehran);
    final preferences = await SharedPreferences.getInstance();

    expect(preferences.getString('weather_selected_source_kind'), 'location');
    expect(preferences.getInt('weather_selected_location_id'), 2);
    expect(preferences.getInt('weather_selected_farm_id'), isNull);
    expect(controller.state.isFarmSource, isFalse);
  });
}

class _WeatherRepository implements WeatherRepository {
  _WeatherRepository(this.locations);

  final List<WeatherLocationModel> locations;

  @override
  Future<List<WeatherLocationModel>> listLocations() async => locations;

  @override
  Future<WeatherSnapshotModel?> current(int locationId) async =>
      WeatherSnapshotModel(
        id: locationId,
        locationId: locationId,
        provider: 'test',
        observedAt: '2026-08-02T08:00:00Z',
        temperatureC: '25',
      );

  @override
  Future<List<WeatherForecastModel>> forecast(int locationId) async => const [];

  @override
  Future<List<WeatherAlertModel>> alerts(int locationId) async => const [];

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FarmRepository implements FarmRepository {
  @override
  Future<List<FarmModel>> farms() async => const [
    FarmModel(id: 10, name: 'My farm', status: 'active'),
  ];

  @override
  Future<List<FarmPlotModel>> plots(int farmId) async => const [
    FarmPlotModel(
      id: 20,
      farmId: 10,
      name: 'North plot',
      areaSqm: 1000,
      status: 'active',
      latitude: 35.7,
      longitude: 51.4,
    ),
  ];

  @override
  Future<FarmWeatherModel> weather(
    int farmId,
    int plotId, {
    bool refresh = false,
  }) async => const FarmWeatherModel(
    refreshed: false,
    snapshot: {
      'provider': 'test',
      'temperature_c': '24.5',
      'observed_at': '2026-08-02T08:00:00Z',
    },
    temperatureC: 24.5,
    forecasts: [],
    alerts: [],
  );

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
