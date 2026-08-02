import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:farm_net/features/weather/domain/weather_chart_data.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final now = DateTime(2026, 8, 2, 6);

  test('builds a sorted 24-hour chart from real forecast values', () {
    final data = WeatherChartData.fromForecasts([
      _row(now.add(const Duration(hours: 9)), probability: '0.4'),
      _row(now.add(const Duration(hours: 3)), probability: '35'),
      _row(now.add(const Duration(hours: 27)), probability: '0.8'),
    ], now: now);

    expect(data.points, hasLength(2));
    expect(data.points.first.time, now.add(const Duration(hours: 3)));
    expect(data.points.first.rainProbability, 35);
    expect(data.points.last.rainProbability, 40);
    expect(data.points.first.temperature, 22.5);
    expect(data.points.first.windSpeed, 3.2);
  });

  test('ignores invalid timestamps and preserves missing measurements', () {
    final data = WeatherChartData.fromForecasts([
      _row(now.add(const Duration(hours: 3)), temperature: null),
      const WeatherForecastModel(
        id: 2,
        locationId: 1,
        provider: 'test',
        forecastType: 'hourly',
        forecastTime: 'invalid',
      ),
    ], now: now);

    expect(data.points, hasLength(1));
    expect(data.points.single.temperature, isNull);
  });
}

WeatherForecastModel _row(
  DateTime time, {
  String? probability = '0.2',
  String? temperature = '22.5',
}) => WeatherForecastModel(
  id: 1,
  locationId: 1,
  provider: 'test',
  forecastType: 'hourly',
  forecastTime: time.toIso8601String(),
  temperatureC: temperature,
  humidityPercent: '55',
  precipitationMm: '0.4',
  precipitationProbability: probability,
  windSpeedMps: '3.2',
);
