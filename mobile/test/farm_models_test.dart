import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('farm and plot parse decimal strings without losing ownership ids', () {
    final farm = FarmModel.fromJson({
      'id': 4,
      'name': 'مزرعه شمالی',
      'status': 'active',
      'declared_area_sqm': '12500.50',
    });
    final plot = FarmPlotModel.fromJson({
      'id': 8,
      'farm_id': 4,
      'name': 'قطعه یک',
      'area_sqm': '2500.25',
      'status': 'active',
      'latitude': '35.1234567',
      'longitude': '51.1234567',
    });

    expect(farm.declaredAreaSqm, 12500.5);
    expect(plot.farmId, farm.id);
    expect(plot.latitude, closeTo(35.1234567, 0.0000001));
  });

  test('crop cycle parses lifecycle dates and status', () {
    final cycle = CropCycleModel.fromJson({
      'id': 3,
      'plot_id': 8,
      'crop_id': 2,
      'status': 'active',
      'planned_start_date': '2026-03-01',
      'planned_end_date': '2026-08-01',
      'actual_start_date': '2026-03-02',
      'actual_end_date': null,
    });
    expect(cycle.status, 'active');
    expect(cycle.actualStartDate, DateTime(2026, 3, 2));
    expect(cycle.actualEndDate, isNull);
  });

  test('weather parser consumes privacy-safe contextual contract', () {
    final weather = FarmWeatherModel.fromJson({
      'refreshed': true,
      'snapshot': {'temperature_c': '22.5', 'condition_text': 'صاف'},
      'forecasts': [
        {'forecast_type': 'hourly'},
      ],
      'alerts': [
        {'alert_type': 'strong_wind'},
      ],
    });
    expect(weather.temperatureC, 22.5);
    expect(weather.forecasts, hasLength(1));
    expect(weather.alerts, hasLength(1));
  });

  test('measurement unit parser supports friendly harvest selection', () {
    final unit = MeasurementUnitModel.fromJson({
      'id': 2,
      'title': 'کیلوگرم',
      'symbol': 'kg',
      'dimension': 'mass',
    });
    expect(unit.title, 'کیلوگرم');
    expect(unit.dimension, 'mass');
  });
}
