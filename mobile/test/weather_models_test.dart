import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';

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
}
