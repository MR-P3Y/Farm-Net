import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/weather/state/weather_state.dart';

void main() {
  test('weather alert parses the complete public contract', () {
    final alert = WeatherAlertModel.fromJson({
      'id': 12,
      'location_id': 4,
      'rule_id': 8,
      'alert_type': 'strong_wind',
      'severity': 'high',
      'status': 'active',
      'title': 'هشدار باد شدید',
      'body': 'سرعت باد بالا است.',
      'starts_at': '2026-08-01T15:00:00Z',
      'ends_at': '2026-08-01T18:00:00Z',
      'is_active': true,
      'payload_json': {'wind_speed_mps': '13.5', 'forecast_id': 91},
      'created_at': '2026-08-01T12:00:00Z',
      'updated_at': '2026-08-01T12:00:00Z',
    });

    expect(alert.id, 12);
    expect(alert.ruleId, 8);
    expect(alert.endsAt, '2026-08-01T18:00:00Z');
    expect(alert.isActive, isTrue);
    expect(alert.isHighPriority, isTrue);
    expect(alert.isCritical, isFalse);
    expect(alert.payload['wind_speed_mps'], '13.5');
  });

  test('weather alert safely defaults optional payload and end time', () {
    final alert = WeatherAlertModel.fromJson({
      'id': 13,
      'location_id': 4,
      'alert_type': 'frost',
      'severity': 'critical',
      'status': 'active',
      'title': 'هشدار سرمازدگی',
      'body': 'از محصول محافظت کنید.',
      'starts_at': '2026-08-02T00:00:00Z',
      'is_active': true,
    });

    expect(alert.ruleId, isNull);
    expect(alert.endsAt, isNull);
    expect(alert.payload, isEmpty);
    expect(alert.isCritical, isTrue);
    expect(alert.isHighPriority, isTrue);
  });

  test('farm weather contracts adapt to the shared weather presentation', () {
    final snapshot = WeatherSnapshotModel.fromFarmJson({
      'provider': 'openweather',
      'temperature_c': '27.4',
      'humidity_percent': '41',
      'wind_speed_mps': '2.8',
      'condition_text': 'Clear',
      'observed_at': '2026-08-01T10:00:00Z',
    });
    final forecast = WeatherForecastModel.fromFarmJson({
      'provider': 'openweather',
      'forecast_type': 'hourly',
      'forecast_time': '2026-08-01T12:00:00Z',
      'temperature_c': '29.0',
      'precipitation_probability': '0.2',
    });
    final alert = WeatherAlertModel.fromFarmJson({
      'id': 44,
      'alert_type': 'heat',
      'severity': 'high',
      'title': 'هشدار گرما',
      'body': 'دمای بالا پیش‌بینی شده است.',
      'starts_at': '2026-08-01T12:00:00Z',
      'ends_at': null,
    });

    expect(snapshot.temperatureC, '27.4');
    expect(snapshot.provider, 'openweather');
    expect(forecast.forecastType, 'hourly');
    expect(forecast.precipitationProbability, '0.2');
    expect(alert.status, 'active');
    expect(alert.isActive, isTrue);
    expect(alert.isHighPriority, isTrue);
  });

  test('farm weather context retains its complete snapshot for shared UI', () {
    final value = FarmWeatherModel.fromJson({
      'refreshed': true,
      'snapshot': {
        'provider': 'openweather',
        'temperature_c': '25.1',
        'condition_text': 'Clouds',
        'observed_at': '2026-08-01T09:00:00Z',
      },
      'forecasts': <Map<String, dynamic>>[],
      'alerts': <Map<String, dynamic>>[],
    });

    expect(value.snapshot?['provider'], 'openweather');
    expect(value.temperatureC, 25.1);
    expect(value.conditionText, 'Clouds');
  });

  test('weather state identifies and clears a selected farm plot source', () {
    final selected = WeatherState.initial().copyWith(
      selectedFarmId: 4,
      selectedPlotId: 7,
      selectedFarmName: 'Farm A',
      selectedPlotName: 'North plot',
    );

    expect(selected.isFarmSource, isTrue);
    expect(selected.farmDisplayName, 'Farm A · North plot');
    expect(selected.copyWith(clearFarmSource: true).isFarmSource, isFalse);
  });
}
