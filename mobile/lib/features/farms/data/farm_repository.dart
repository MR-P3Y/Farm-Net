import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'farm_api.dart';
import 'farm_models.dart';

final farmRepositoryProvider = Provider<FarmRepository>(
  (ref) => FarmRepository(api: FarmApi()),
);

class FarmRepository {
  const FarmRepository({required FarmApi api}) : _api = api;
  final FarmApi _api;

  Future<List<FarmModel>> farms() => _api.farms();
  Future<FarmModel> createFarm(Map<String, dynamic> value) =>
      _api.createFarm(value);
  Future<List<FarmPlotModel>> plots(int farmId) => _api.plots(farmId);
  Future<FarmPlotModel> createPlot(int farmId, Map<String, dynamic> value) =>
      _api.createPlot(farmId, value);
  Future<List<CropReference>> crops() => _api.crops();
  Future<List<MeasurementUnitModel>> harvestUnits() => _api.harvestUnits();
  Future<List<CropCycleModel>> cycles(int farmId, int plotId) =>
      _api.cycles(farmId, plotId);
  Future<CropCycleModel> createCycle(
    int farmId,
    int plotId,
    Map<String, dynamic> value,
  ) => _api.createCycle(farmId, plotId, value);
  Future<CropCycleModel> transition(
    int farmId,
    int plotId,
    int cycleId,
    String action,
  ) => _api.transitionCycle(farmId, plotId, cycleId, action);
  Future<List<FarmOperationModel>> operations(int farmId, int plotId, int id) =>
      _api.operations(farmId, plotId, id);
  Future<void> createOperation(
    int farmId,
    int plotId,
    int id,
    Map<String, dynamic> value,
  ) => _api.createOperation(farmId, plotId, id, value);
  Future<List<FarmHarvestModel>> harvests(int farmId, int plotId, int id) =>
      _api.harvests(farmId, plotId, id);
  Future<void> createHarvest(
    int farmId,
    int plotId,
    int id,
    Map<String, dynamic> value,
  ) => _api.createHarvest(farmId, plotId, id, value);
  Future<FarmWeatherModel> weather(
    int farmId,
    int plotId, {
    bool refresh = false,
  }) => _api.weather(farmId, plotId, refresh: refresh);
}
