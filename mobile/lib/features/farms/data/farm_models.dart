class FarmModel {
  const FarmModel({
    required this.id,
    required this.name,
    required this.status,
    this.description,
    this.declaredAreaSqm,
    this.archivedAt,
    this.archiveReason,
    this.canEdit = true,
    this.canArchive = true,
    this.canRestore = false,
  });

  final int id;
  final String name;
  final String status;
  final String? description;
  final double? declaredAreaSqm;
  final DateTime? archivedAt;
  final String? archiveReason;
  final bool canEdit;
  final bool canArchive;
  final bool canRestore;

  bool get isArchived => status == 'archived';

  factory FarmModel.fromJson(Map<String, dynamic> json) {
    final status = json['status'] as String;
    final isActive = status == 'active';
    return FarmModel(
      id: json['id'] as int,
      name: json['name'] as String,
      status: status,
      description: json['description'] as String?,
      declaredAreaSqm: _double(json['declared_area_sqm']),
      archivedAt: _date(json['archived_at']),
      archiveReason: json['archive_reason'] as String?,
      canEdit: json['can_edit'] as bool? ?? isActive,
      canArchive: json['can_archive'] as bool? ?? isActive,
      canRestore: json['can_restore'] as bool? ?? !isActive,
    );
  }
}

class FarmPlotModel {
  const FarmPlotModel({
    required this.id,
    required this.farmId,
    required this.name,
    required this.areaSqm,
    required this.status,
    this.description,
    this.latitude,
    this.longitude,
    this.boundary = const [],
  });

  final int id;
  final int farmId;
  final String name;
  final double areaSqm;
  final String status;
  final String? description;
  final double? latitude;
  final double? longitude;
  final List<FarmGeoPointModel> boundary;

  bool get hasLocation => latitude != null && longitude != null;

  bool get hasBoundary => boundary.length >= 4;

  factory FarmPlotModel.fromJson(Map<String, dynamic> json) => FarmPlotModel(
    id: json['id'] as int,
    farmId: json['farm_id'] as int,
    name: json['name'] as String,
    areaSqm: _double(json['area_sqm']) ?? 0,
    status: json['status'] as String,
    description: json['description'] as String?,
    latitude: _double(json['latitude']),
    longitude: _double(json['longitude']),
    boundary: (json['boundary'] as List? ?? const [])
        .whereType<Map>()
        .map((point) => FarmGeoPointModel.fromJson(point.cast()))
        .toList(growable: false),
  );
}

class FarmGeoPointModel {
  const FarmGeoPointModel({required this.latitude, required this.longitude});

  final double latitude;
  final double longitude;

  factory FarmGeoPointModel.fromJson(Map<String, dynamic> json) =>
      FarmGeoPointModel(
        latitude: _double(json['latitude']) ?? 0,
        longitude: _double(json['longitude']) ?? 0,
      );

  Map<String, double> toJson() => {
    'latitude': latitude,
    'longitude': longitude,
  };
}

class CropReference {
  const CropReference({required this.id, required this.title});
  final int id;
  final String title;

  factory CropReference.fromJson(Map<String, dynamic> json) =>
      CropReference(id: json['id'] as int, title: json['title'] as String);
}

class MeasurementUnitModel {
  const MeasurementUnitModel({
    required this.id,
    required this.title,
    required this.symbol,
    required this.dimension,
  });
  final int id;
  final String title;
  final String symbol;
  final String dimension;

  factory MeasurementUnitModel.fromJson(Map<String, dynamic> json) =>
      MeasurementUnitModel(
        id: json['id'] as int,
        title: json['title'] as String,
        symbol: json['symbol'] as String,
        dimension: json['dimension'] as String,
      );
}

class CropCycleModel {
  const CropCycleModel({
    required this.id,
    required this.plotId,
    required this.cropId,
    required this.status,
    required this.plannedStartDate,
    required this.plannedEndDate,
    this.title,
    this.actualStartDate,
    this.actualEndDate,
  });

  final int id;
  final int plotId;
  final int cropId;
  final String status;
  final String? title;
  final DateTime plannedStartDate;
  final DateTime plannedEndDate;
  final DateTime? actualStartDate;
  final DateTime? actualEndDate;

  factory CropCycleModel.fromJson(Map<String, dynamic> json) => CropCycleModel(
    id: json['id'] as int,
    plotId: json['plot_id'] as int,
    cropId: json['crop_id'] as int,
    status: json['status'] as String,
    title: json['title'] as String?,
    plannedStartDate: DateTime.parse(json['planned_start_date'] as String),
    plannedEndDate: DateTime.parse(json['planned_end_date'] as String),
    actualStartDate: _date(json['actual_start_date']),
    actualEndDate: _date(json['actual_end_date']),
  );
}

class FarmOperationModel {
  const FarmOperationModel({
    required this.id,
    required this.type,
    required this.title,
    required this.occurredOn,
    this.notes,
  });
  final int id;
  final String type;
  final String title;
  final DateTime occurredOn;
  final String? notes;

  factory FarmOperationModel.fromJson(Map<String, dynamic> json) =>
      FarmOperationModel(
        id: json['id'] as int,
        type: json['operation_type'] as String,
        title: json['title'] as String,
        occurredOn: DateTime.parse(json['occurred_on'] as String),
        notes: json['notes'] as String?,
      );
}

class FarmHarvestModel {
  const FarmHarvestModel({
    required this.id,
    required this.harvestedOn,
    required this.quantity,
    required this.unitSymbol,
    this.qualityGrade,
  });
  final int id;
  final DateTime harvestedOn;
  final double quantity;
  final String unitSymbol;
  final String? qualityGrade;

  factory FarmHarvestModel.fromJson(Map<String, dynamic> json) =>
      FarmHarvestModel(
        id: json['id'] as int,
        harvestedOn: DateTime.parse(json['harvested_on'] as String),
        quantity: _double(json['quantity']) ?? 0,
        unitSymbol: json['unit_symbol'] as String,
        qualityGrade: json['quality_grade'] as String?,
      );
}

class FarmWeatherModel {
  const FarmWeatherModel({
    required this.refreshed,
    required this.forecasts,
    required this.alerts,
    this.snapshot,
    this.temperatureC,
    this.conditionText,
  });
  final bool refreshed;
  final Map<String, dynamic>? snapshot;
  final double? temperatureC;
  final String? conditionText;
  final List<Map<String, dynamic>> forecasts;
  final List<Map<String, dynamic>> alerts;

  factory FarmWeatherModel.fromJson(Map<String, dynamic> json) {
    final snapshot = json['snapshot'] as Map<String, dynamic>?;
    return FarmWeatherModel(
      refreshed: json['refreshed'] as bool? ?? false,
      snapshot: snapshot == null ? null : Map<String, dynamic>.from(snapshot),
      temperatureC: _double(snapshot?['temperature_c']),
      conditionText: snapshot?['condition_text'] as String?,
      forecasts:
          (json['forecasts'] as List? ?? const [])
              .whereType<Map<String, dynamic>>()
              .toList(),
      alerts:
          (json['alerts'] as List? ?? const [])
              .whereType<Map<String, dynamic>>()
              .toList(),
    );
  }
}

double? _double(Object? value) =>
    value == null ? null : double.tryParse(value.toString());

DateTime? _date(Object? value) =>
    value == null ? null : DateTime.tryParse(value.toString());
