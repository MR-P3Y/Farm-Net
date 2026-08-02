import 'dart:math' as math;

enum FarmCalculatorType {
  seed('seed'),
  irrigation('irrigation'),
  fertilizer('fertilizer'),
  spraying('spraying'),
  costProfit('cost_profit'),
  unitConversion('unit_conversion'),
  pumpFuel('pump_fuel');

  const FarmCalculatorType(this.apiValue);

  final String apiValue;

  static FarmCalculatorType fromApi(String value) => values.firstWhere(
    (item) => item.apiValue == value,
    orElse: () => FarmCalculatorType.unitConversion,
  );
}

class FarmCalculationResult {
  const FarmCalculationResult({required this.values, required this.units});

  final Map<String, double> values;
  final Map<String, String> units;
}

class FarmCalculatorEngine {
  const FarmCalculatorEngine._();

  static const formulaVersion = '1.0';

  static const requiredInputs = <FarmCalculatorType, Set<String>>{
    FarmCalculatorType.seed: {
      'area_sqm',
      'row_spacing_m',
      'plant_spacing_m',
      'germination_percent',
      'reserve_percent',
    },
    FarmCalculatorType.irrigation: {
      'area_sqm',
      'depth_mm',
      'efficiency_percent',
      'flow_lpm',
    },
    FarmCalculatorType.fertilizer: {
      'area_sqm',
      'rate_kg_per_hectare',
      'bag_size_kg',
    },
    FarmCalculatorType.spraying: {
      'area_sqm',
      'water_rate_l_per_hectare',
      'product_rate_ml_per_l',
      'tank_capacity_l',
    },
    FarmCalculatorType.costProfit: {
      'total_cost_toman',
      'expected_yield_kg',
      'price_per_kg_toman',
      'area_sqm',
    },
    FarmCalculatorType.unitConversion: {'value', 'factor'},
    FarmCalculatorType.pumpFuel: {
      'flow_lpm',
      'target_volume_l',
      'fuel_l_per_hour',
      'fuel_price_toman',
    },
  };

  static FarmCalculationResult calculate(
    FarmCalculatorType type,
    Map<String, double> values,
  ) {
    final expected = requiredInputs[type]!;
    if (values.keys.toSet().difference(expected).isNotEmpty ||
        expected.difference(values.keys.toSet()).isNotEmpty) {
      throw const FormatException('Calculator inputs do not match formula 1.0');
    }
    for (final entry in values.entries) {
      if (!entry.value.isFinite ||
          entry.value < 0 ||
          entry.value > 1000000000000000) {
        throw FormatException('Invalid calculator value: ${entry.key}');
      }
    }

    switch (type) {
      case FarmCalculatorType.seed:
        _positive(values, ['area_sqm', 'row_spacing_m', 'plant_spacing_m']);
        _percent(values, 'germination_percent', allowZero: false);
        _percent(values, 'reserve_percent', allowZero: true);
        final plants =
            values['area_sqm']! /
            (values['row_spacing_m']! * values['plant_spacing_m']!);
        final seeds =
            plants /
            (values['germination_percent']! / 100) *
            (1 + values['reserve_percent']! / 100);
        return FarmCalculationResult(
          values: {'plant_count': _ceil(plants), 'seed_count': _ceil(seeds)},
          units: const {'plant_count': 'count', 'seed_count': 'count'},
        );

      case FarmCalculatorType.irrigation:
        _positive(values, ['area_sqm', 'depth_mm', 'flow_lpm']);
        _percent(values, 'efficiency_percent', allowZero: false);
        final volume =
            values['area_sqm']! *
            values['depth_mm']! /
            (values['efficiency_percent']! / 100);
        return FarmCalculationResult(
          values: {
            'volume_l': _round(volume),
            'duration_minutes': _round(volume / values['flow_lpm']!),
          },
          units: const {'volume_l': 'L', 'duration_minutes': 'min'},
        );

      case FarmCalculatorType.fertilizer:
        _positive(values, ['area_sqm', 'rate_kg_per_hectare', 'bag_size_kg']);
        final total =
            values['area_sqm']! / 10000 * values['rate_kg_per_hectare']!;
        return FarmCalculationResult(
          values: {
            'total_kg': _round(total),
            'bag_count': _ceil(total / values['bag_size_kg']!),
          },
          units: const {'total_kg': 'kg', 'bag_count': 'bag'},
        );

      case FarmCalculatorType.spraying:
        _positive(values, [
          'area_sqm',
          'water_rate_l_per_hectare',
          'product_rate_ml_per_l',
          'tank_capacity_l',
        ]);
        final water =
            values['area_sqm']! / 10000 * values['water_rate_l_per_hectare']!;
        return FarmCalculationResult(
          values: {
            'water_l': _round(water),
            'product_ml': _round(water * values['product_rate_ml_per_l']!),
            'tank_count': _ceil(water / values['tank_capacity_l']!),
          },
          units: const {
            'water_l': 'L',
            'product_ml': 'mL',
            'tank_count': 'tank',
          },
        );

      case FarmCalculatorType.costProfit:
        _positive(values, ['expected_yield_kg', 'area_sqm']);
        final revenue =
            values['expected_yield_kg']! * values['price_per_kg_toman']!;
        final cost = values['total_cost_toman']!;
        return FarmCalculationResult(
          values: {
            'expected_revenue_toman': _round(revenue, 2),
            'profit_toman': _round(revenue - cost, 2),
            'break_even_price_per_kg_toman': _round(
              cost / values['expected_yield_kg']!,
              2,
            ),
            'cost_per_sqm_toman': _round(cost / values['area_sqm']!, 2),
          },
          units: const {
            'expected_revenue_toman': 'TOMAN',
            'profit_toman': 'TOMAN',
            'break_even_price_per_kg_toman': 'TOMAN/kg',
            'cost_per_sqm_toman': 'TOMAN/m²',
          },
        );

      case FarmCalculatorType.unitConversion:
        _positive(values, ['factor']);
        return FarmCalculationResult(
          values: {
            'converted_value': _round(values['value']! * values['factor']!),
          },
          units: const {'converted_value': 'selected_unit'},
        );

      case FarmCalculatorType.pumpFuel:
        _positive(values, ['flow_lpm', 'target_volume_l']);
        final duration = values['target_volume_l']! / values['flow_lpm']!;
        final fuel = duration / 60 * values['fuel_l_per_hour']!;
        return FarmCalculationResult(
          values: {
            'duration_minutes': _round(duration),
            'fuel_l': _round(fuel),
            'fuel_cost_toman': _round(fuel * values['fuel_price_toman']!, 2),
          },
          units: const {
            'duration_minutes': 'min',
            'fuel_l': 'L',
            'fuel_cost_toman': 'TOMAN',
          },
        );
    }
  }

  static void _positive(Map<String, double> values, List<String> keys) {
    for (final key in keys) {
      if (values[key]! <= 0) {
        throw FormatException('Calculator value must be positive: $key');
      }
    }
  }

  static void _percent(
    Map<String, double> values,
    String key, {
    required bool allowZero,
  }) {
    final value = values[key]!;
    if (value > 100 || value < (allowZero ? 0 : 0.000001)) {
      throw FormatException('Calculator percentage is invalid: $key');
    }
  }

  static double _round(double value, [int places = 6]) {
    final factor = math.pow(10, places).toDouble();
    return (value * factor).roundToDouble() / factor;
  }

  static double _ceil(double value) {
    final nearest = value.roundToDouble();
    final tolerance = math.max(1, value.abs()) * 1e-12;
    return (value - nearest).abs() <= tolerance
        ? nearest
        : value.ceilToDouble();
  }
}

class UnitConversionOption {
  const UnitConversionOption({
    required this.code,
    required this.fromUnit,
    required this.toUnit,
    required this.factor,
  });

  final String code;
  final String fromUnit;
  final String toUnit;
  final double factor;
}

const farmUnitConversions = <UnitConversionOption>[
  UnitConversionOption(
    code: 'sqm_to_hectare',
    fromUnit: 'm²',
    toUnit: 'ha',
    factor: 0.0001,
  ),
  UnitConversionOption(
    code: 'hectare_to_sqm',
    fromUnit: 'ha',
    toUnit: 'm²',
    factor: 10000,
  ),
  UnitConversionOption(
    code: 'liter_to_cubic_metre',
    fromUnit: 'L',
    toUnit: 'm³',
    factor: 0.001,
  ),
  UnitConversionOption(
    code: 'cubic_metre_to_liter',
    fromUnit: 'm³',
    toUnit: 'L',
    factor: 1000,
  ),
  UnitConversionOption(
    code: 'kg_to_ton',
    fromUnit: 'kg',
    toUnit: 'ton',
    factor: 0.001,
  ),
  UnitConversionOption(
    code: 'ton_to_kg',
    fromUnit: 'ton',
    toUnit: 'kg',
    factor: 1000,
  ),
  UnitConversionOption(
    code: 'lpm_to_m3h',
    fromUnit: 'L/min',
    toUnit: 'm³/h',
    factor: 0.06,
  ),
  UnitConversionOption(
    code: 'm3h_to_lpm',
    fromUnit: 'm³/h',
    toUnit: 'L/min',
    factor: 16.6666666667,
  ),
];
