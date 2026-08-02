import 'package:farm_net/features/farms/data/farm_repository.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:farm_net/features/weather/data/weather_repository.dart';
import 'package:farm_net/features/weather/state/weather_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  const firstGps = WeatherLocationModel(
    id: 11,
    displayName: 'Current location',
    locationType: 'gps',
    latitude: '35.7000',
    longitude: '51.4000',
    isActive: true,
  );
  const duplicateGps = WeatherLocationModel(
    id: 12,
    displayName: 'Current location',
    locationType: 'gps',
    latitude: '35.7004',
    longitude: '51.4005',
    isActive: true,
  );

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('load exposes only one saved GPS location', () async {
    final repository = _WeatherRepository([firstGps, duplicateGps]);
    final controller = WeatherController(
      repository: repository,
      farmRepository: _FarmRepository(),
    );

    await controller.load();

    expect(
      controller.state.locations.where((item) => item.locationType == 'gps'),
      hasLength(1),
    );
  });

  test(
    'generic nearby GPS source is resolved once without adding a row',
    () async {
      final repository = _WeatherRepository([firstGps]);
      final controller = WeatherController(
        repository: repository,
        farmRepository: _FarmRepository(),
      );
      await controller.load();

      await controller.createGpsLocation(
        latitude: 35.7008,
        longitude: 51.4007,
        displayName: 'Current location',
      );

      expect(repository.createCount, 1);
      expect(controller.state.selectedLocation?.id, firstGps.id);
    },
  );
}

class _WeatherRepository implements WeatherRepository {
  _WeatherRepository(this.locations);

  final List<WeatherLocationModel> locations;
  int createCount = 0;

  @override
  Future<List<WeatherLocationModel>> listLocations() async => locations;

  @override
  Future<WeatherSnapshotModel?> current(int locationId) async => null;

  @override
  Future<List<WeatherForecastModel>> forecast(int locationId) async => const [];

  @override
  Future<List<WeatherAlertModel>> alerts(int locationId) async => const [];

  @override
  Future<void> refresh({required int locationId, String? provider}) async {}

  @override
  Future<WeatherLocationModel> createGpsLocation({
    required double latitude,
    required double longitude,
    String? displayName,
    String? timezone,
  }) async {
    createCount += 1;
    return locations.first;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FarmRepository implements FarmRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
