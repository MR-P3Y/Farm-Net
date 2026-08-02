import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/home/data/home_dashboard_models.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('dashboard weather keeps independent city and Farm Plot sources', () {
    const location = WeatherLocationModel(
      id: 1,
      displayName: 'Tehran',
      locationType: 'city',
      latitude: '35.7',
      longitude: '51.4',
      isActive: true,
    );
    const farm = FarmModel(id: 4, name: 'North farm', status: 'active');
    const plot = FarmPlotModel(
      id: 7,
      farmId: 4,
      name: 'Wheat plot',
      areaSqm: 1000,
      status: 'active',
      latitude: 36,
      longitude: 52,
    );
    final data = HomeWeatherData(
      sources: [
        HomeWeatherSource.location(location: location),
        HomeWeatherSource.farm(farm: farm, plot: plot),
      ],
    );

    expect(data.effectiveSources, hasLength(2));
    expect(data.effectiveSources.map((item) => item.key).toSet(), hasLength(2));
  });
}
