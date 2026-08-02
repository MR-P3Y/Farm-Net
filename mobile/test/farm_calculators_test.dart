import 'package:farm_net/features/toolbox/domain/farm_calculators.dart';
import 'package:farm_net/features/toolbox/domain/toolbox_number_input.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('seed calculator accounts for spacing germination and reserve', () {
    final result = FarmCalculatorEngine.calculate(FarmCalculatorType.seed, {
      'area_sqm': 10000,
      'row_spacing_m': 1,
      'plant_spacing_m': .5,
      'germination_percent': 80,
      'reserve_percent': 10,
    });
    expect(result.values['plant_count'], 20000);
    expect(result.values['seed_count'], 27500);
  });

  test('irrigation calculator returns gross volume and pump duration', () {
    final result = FarmCalculatorEngine.calculate(
      FarmCalculatorType.irrigation,
      {
        'area_sqm': 1000,
        'depth_mm': 10,
        'efficiency_percent': 80,
        'flow_lpm': 100,
      },
    );
    expect(result.values['volume_l'], 12500);
    expect(result.values['duration_minutes'], 125);
  });

  test('fertilizer and spraying round purchase containers upward', () {
    final fertilizer = FarmCalculatorEngine.calculate(
      FarmCalculatorType.fertilizer,
      {'area_sqm': 5000, 'rate_kg_per_hectare': 200, 'bag_size_kg': 30},
    );
    final spraying =
        FarmCalculatorEngine.calculate(FarmCalculatorType.spraying, {
          'area_sqm': 10000,
          'water_rate_l_per_hectare': 500,
          'product_rate_ml_per_l': 2,
          'tank_capacity_l': 200,
        });
    expect(fertilizer.values['total_kg'], 100);
    expect(fertilizer.values['bag_count'], 4);
    expect(spraying.values['product_ml'], 1000);
    expect(spraying.values['tank_count'], 3);
  });

  test('cost and pump calculators expose actionable totals', () {
    final profit =
        FarmCalculatorEngine.calculate(FarmCalculatorType.costProfit, {
          'total_cost_toman': 1000000,
          'expected_yield_kg': 1000,
          'price_per_kg_toman': 1500,
          'area_sqm': 10000,
        });
    final pump = FarmCalculatorEngine.calculate(FarmCalculatorType.pumpFuel, {
      'flow_lpm': 100,
      'target_volume_l': 6000,
      'fuel_l_per_hour': 2,
      'fuel_price_toman': 10000,
    });
    expect(profit.values['profit_toman'], 500000);
    expect(profit.values['break_even_price_per_kg_toman'], 1000);
    expect(pump.values['duration_minutes'], 60);
    expect(pump.values['fuel_cost_toman'], 20000);
  });

  test('unit conversion uses a bounded fixed conversion registry', () {
    final option = farmUnitConversions.first;
    final result = FarmCalculatorEngine.calculate(
      FarmCalculatorType.unitConversion,
      {'value': 10000, 'factor': option.factor},
    );
    expect(option.code, 'sqm_to_hectare');
    expect(result.values['converted_value'], 1);
  });

  test('unsafe percentages and incomplete formula inputs are rejected', () {
    expect(
      () => FarmCalculatorEngine.calculate(FarmCalculatorType.seed, {
        'area_sqm': 100,
        'row_spacing_m': 1,
        'plant_spacing_m': 1,
        'germination_percent': 101,
        'reserve_percent': 0,
      }),
      throwsFormatException,
    );
    expect(
      () => FarmCalculatorEngine.calculate(FarmCalculatorType.unitConversion, {
        'value': 1,
      }),
      throwsFormatException,
    );
  });

  test('toolbox numeric input accepts Persian and Arabic digits', () {
    expect(parseToolboxNumber('۱۲٬۳۴۵٫۵'), 12345.5);
    expect(parseToolboxNumber('١٢٣.٥'), 123.5);
  });
}
