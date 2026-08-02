import '../../farms/data/farm_models.dart';

class ToolboxContextSelection {
  const ToolboxContextSelection({required this.farm, this.plot, this.cycle});

  final FarmModel farm;
  final FarmPlotModel? plot;
  final CropCycleModel? cycle;

  int get farmId => farm.id;
  int? get plotId => plot?.id;
  int? get cycleId => cycle?.id;

  double? get areaSqm => plot?.areaSqm ?? farm.declaredAreaSqm;
}
