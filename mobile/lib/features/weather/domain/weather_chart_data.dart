import '../data/weather_models.dart';

class WeatherChartPoint {
  const WeatherChartPoint({
    required this.time,
    this.temperature,
    this.humidity,
    this.rainProbability,
    this.precipitationMm,
    this.windSpeed,
  });

  final DateTime time;
  final double? temperature;
  final double? humidity;
  final double? rainProbability;
  final double? precipitationMm;
  final double? windSpeed;
}

class WeatherChartData {
  const WeatherChartData(this.points);

  final List<WeatherChartPoint> points;

  factory WeatherChartData.fromForecasts(
    List<WeatherForecastModel> forecasts, {
    DateTime? now,
    Duration horizon = const Duration(hours: 24),
  }) {
    final start = (now ?? DateTime.now()).toLocal();
    final end = start.add(horizon);
    final points = <WeatherChartPoint>[];
    for (final row in forecasts) {
      final time = DateTime.tryParse(row.forecastTime)?.toLocal();
      if (time == null || time.isBefore(start) || time.isAfter(end)) continue;
      final probability = _number(row.precipitationProbability);
      points.add(
        WeatherChartPoint(
          time: time,
          temperature: _number(row.temperatureC),
          humidity: _number(row.humidityPercent),
          rainProbability:
              probability == null
                  ? null
                  : (probability <= 1 ? probability * 100 : probability).clamp(
                    0,
                    100,
                  ),
          precipitationMm: _number(row.precipitationMm),
          windSpeed: _number(row.windSpeedMps),
        ),
      );
    }
    points.sort((a, b) => a.time.compareTo(b.time));
    return WeatherChartData(List.unmodifiable(points));
  }

  static double? _number(String? value) => double.tryParse(value ?? '');
}
