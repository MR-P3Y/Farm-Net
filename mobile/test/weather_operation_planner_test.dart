import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:farm_net/features/weather/domain/weather_operation_planner.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const planner = WeatherOperationPlanner();
  final now = DateTime(2026, 8, 2, 6);

  test(
    'planner returns one transparent plan for every supported operation',
    () {
      final plans = planner.plan(const [], now: now);

      expect(plans, hasLength(WeatherOperationType.values.length));
      expect(plans.every((plan) => !plan.isSuitable), isTrue);
      expect(
        plans.every(
          (plan) =>
              plan.reasonCodes.length == 1 &&
              plan.reasonCodes.single == 'forecast_unavailable',
        ),
        isTrue,
      );
    },
  );

  test('spraying rejects backend-aligned wind and rain boundaries', () {
    final plans = planner.plan([
      _forecast(
        time: now.add(const Duration(hours: 3)),
        wind: 8,
        rainProbability: 0.6,
      ),
    ], now: now);
    final spraying = plans.singleWhere(
      (plan) => plan.operation == WeatherOperationType.spraying,
    );

    expect(spraying.isSuitable, isFalse);
    expect(spraying.reasonCodes, contains('wind_blocking'));
    expect(spraying.reasonCodes, contains('rain_probability_blocking'));
  });

  test('planner selects and extends consecutive calm spraying slots', () {
    final first = now.add(const Duration(hours: 3));
    final plans = planner.plan([
      _forecast(time: first, wind: 2, rainProbability: 0.05),
      _forecast(
        time: first.add(const Duration(hours: 3)),
        wind: 2.5,
        rainProbability: 0.1,
      ),
      _forecast(
        time: first.add(const Duration(hours: 6)),
        wind: 9,
        rainProbability: 0.1,
      ),
    ], now: now);
    final spraying = plans.singleWhere(
      (plan) => plan.operation == WeatherOperationType.spraying,
    );

    expect(spraying.isSuitable, isTrue);
    expect(spraying.score, 100);
    expect(spraying.startsAt, first);
    expect(spraying.endsAt, first.add(const Duration(hours: 6)));
    expect(spraying.reasonCodes, ['conditions_acceptable']);
  });

  test('planner normalizes percentage-form precipitation probability', () {
    final plans = planner.plan([
      _forecast(
        time: now.add(const Duration(hours: 3)),
        wind: 1,
        rainProbability: 60,
      ),
    ], now: now);
    final spraying = plans.singleWhere(
      (plan) => plan.operation == WeatherOperationType.spraying,
    );

    expect(spraying.isSuitable, isFalse);
    expect(spraying.reasonCodes, contains('rain_probability_blocking'));
  });
}

WeatherForecastModel _forecast({
  required DateTime time,
  required double wind,
  required double rainProbability,
  double temperature = 20,
  double humidity = 50,
  double rainMm = 0,
}) {
  return WeatherForecastModel(
    id: 1,
    locationId: 1,
    provider: 'test',
    forecastType: 'hourly',
    forecastTime: time.toIso8601String(),
    temperatureC: temperature.toString(),
    humidityPercent: humidity.toString(),
    precipitationMm: rainMm.toString(),
    precipitationProbability: rainProbability.toString(),
    windSpeedMps: wind.toString(),
  );
}
