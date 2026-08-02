import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../domain/farm_calculators.dart';
import 'toolbox_api.dart';
import 'toolbox_models.dart';

final toolboxRepositoryProvider = Provider<ToolboxRepository>(
  (ref) => ToolboxRepository(api: ToolboxApi()),
);

class ToolboxRepository {
  const ToolboxRepository({required ToolboxApi api}) : _api = api;

  final ToolboxApi _api;

  Future<FarmToolCalculationModel> saveCalculation({
    required int farmId,
    required FarmCalculatorType type,
    required String title,
    required Map<String, double> inputValues,
    required Map<String, String> inputUnits,
    int? plotId,
    int? cycleId,
    String? notes,
  }) => _api.saveCalculation(
    farmId: farmId,
    type: type,
    title: title,
    inputValues: inputValues,
    inputUnits: inputUnits,
    plotId: plotId,
    cycleId: cycleId,
    notes: notes,
  );

  Future<List<FarmToolCalculationModel>> calculations({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _api.calculations(farmId: farmId, plotId: plotId, cycleId: cycleId);

  Future<FarmFinancialEntryModel> createCost({
    required int farmId,
    required Map<String, dynamic> payload,
  }) => _api.createCost(farmId: farmId, payload: payload);

  Future<List<FarmFinancialEntryModel>> costs({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _api.costs(farmId: farmId, plotId: plotId, cycleId: cycleId);

  Future<FarmFinancialSummaryModel> costSummary({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _api.costSummary(farmId: farmId, plotId: plotId, cycleId: cycleId);

  Future<FarmFinancialEntryModel> voidCost({
    required int farmId,
    required int entryId,
    required String reason,
  }) => _api.voidCost(farmId: farmId, entryId: entryId, reason: reason);

  Future<FarmPlanModel> createPlan({
    required int farmId,
    required Map<String, dynamic> payload,
  }) => _api.createPlan(farmId: farmId, payload: payload);

  Future<List<FarmPlanModel>> plans({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _api.plans(farmId: farmId, plotId: plotId, cycleId: cycleId);

  Future<FarmPlanModel> completePlan({
    required int farmId,
    required int planId,
    required bool writeToDiary,
  }) => _api.completePlan(
    farmId: farmId,
    planId: planId,
    writeToDiary: writeToDiary,
  );

  Future<FarmPlanModel> cancelPlan({
    required int farmId,
    required int planId,
    String? reason,
  }) => _api.cancelPlan(farmId: farmId, planId: planId, reason: reason);
}
