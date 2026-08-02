import 'package:farm_net/features/toolbox/data/toolbox_models.dart';
import 'package:farm_net/features/toolbox/domain/farm_calculators.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('saved calculation parses authoritative decimal snapshots', () {
    final value = FarmToolCalculationModel.fromJson({
      'id': 1,
      'farm_id': 2,
      'plot_id': 3,
      'cycle_id': null,
      'calculator_type': 'irrigation',
      'formula_version': '1.0',
      'title': 'نوبت آبیاری',
      'input_values': {'area_sqm': '1000.00'},
      'input_units': {'area_sqm': 'm²'},
      'result_values': {'volume_l': '12500.000000'},
      'result_units': {'volume_l': 'L'},
      'notes': null,
      'created_at': '2026-08-02T03:00:00',
    });
    expect(value.type, FarmCalculatorType.irrigation);
    expect(value.resultValues['volume_l'], 12500);
    expect(value.resultUnits['volume_l'], 'L');
  });

  test('finance and plan models expose lifecycle helpers', () {
    final cost = FarmFinancialEntryModel.fromJson({
      'id': 4,
      'farm_id': 2,
      'plot_id': null,
      'cycle_id': null,
      'entry_type': 'expense',
      'category': 'fuel',
      'amount_toman': '250000.00',
      'occurred_on': '2026-08-02',
      'description': null,
      'voided_at': null,
      'void_reason': null,
      'created_at': '2026-08-02T03:00:00',
    });
    final plan = FarmPlanModel.fromJson({
      'id': 5,
      'farm_id': 2,
      'plot_id': 3,
      'cycle_id': 7,
      'operation_type': 'irrigation',
      'title': 'آبیاری قطعه',
      'planned_for': '2020-01-01',
      'reminder_at': null,
      'reminder_sent_at': null,
      'status': 'planned',
      'notes': null,
      'completed_at': null,
      'cancelled_at': null,
      'cancel_reason': null,
      'farm_operation_id': null,
      'created_at': '2026-08-02T03:00:00',
      'updated_at': '2026-08-02T03:00:00',
    });
    expect(cost.isExpense, isTrue);
    expect(cost.isVoided, isFalse);
    expect(plan.isPlanned, isTrue);
    expect(plan.isOverdue, isTrue);
  });
}
