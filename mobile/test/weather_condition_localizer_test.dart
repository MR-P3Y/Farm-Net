import 'package:farm_net/features/weather/domain/weather_condition_localizer.dart';
import 'package:farm_net/features/weather/data/weather_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('localizes OpenWeather condition codes in Persian', () {
    expect(
      WeatherConditionLocalizer.label(
        isFa: true,
        code: '801',
        text: 'few clouds',
      ),
      'کمی ابری',
    );
    expect(
      WeatherConditionLocalizer.label(
        isFa: true,
        code: '502',
        text: 'heavy intensity rain',
      ),
      'باران شدید',
    );
  });

  test('keeps provider text for English and unknown Persian conditions', () {
    expect(
      WeatherConditionLocalizer.label(
        isFa: false,
        code: '801',
        text: 'few clouds',
      ),
      'few clouds',
    );
    expect(
      WeatherConditionLocalizer.label(isFa: true, text: 'custom condition'),
      'custom condition',
    );
  });

  test('forecast model retains the provider condition code', () {
    final value = WeatherForecastModel.fromJson({
      'id': 1,
      'location_id': 2,
      'provider': 'openweather',
      'forecast_type': 'hourly',
      'forecast_time': '2026-08-02T09:00:00Z',
      'condition_code': '801',
      'condition_text': 'few clouds',
    });

    expect(value.conditionCode, '801');
  });
}
