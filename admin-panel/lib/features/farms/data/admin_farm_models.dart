class AdminFarmSummary {
  const AdminFarmSummary({
    required this.id,
    required this.ownerUserId,
    required this.name,
    required this.status,
    required this.plotsCount,
    required this.cyclesCount,
    required this.createdAt,
    required this.updatedAt,
    this.declaredAreaSqm,
  });

  final int id;
  final int ownerUserId;
  final String name;
  final String status;
  final double? declaredAreaSqm;
  final int plotsCount;
  final int cyclesCount;
  final String createdAt;
  final String updatedAt;

  factory AdminFarmSummary.fromJson(Map<String, dynamic> json) =>
      AdminFarmSummary(
        id: (json['id'] as num).toInt(),
        ownerUserId: (json['owner_user_id'] as num).toInt(),
        name: json['name'] as String,
        status: json['status'] as String,
        declaredAreaSqm: (json['declared_area_sqm'] as num?)?.toDouble(),
        plotsCount: (json['plots_count'] as num).toInt(),
        cyclesCount: (json['cycles_count'] as num).toInt(),
        createdAt: json['created_at'] as String,
        updatedAt: json['updated_at'] as String,
      );
}

class AdminFarmPlot {
  const AdminFarmPlot({
    required this.id,
    required this.name,
    required this.areaSqm,
    required this.status,
    required this.cyclesCount,
    this.provinceId,
    this.cityId,
  });

  final int id;
  final String name;
  final double areaSqm;
  final String status;
  final int? provinceId;
  final int? cityId;
  final int cyclesCount;

  factory AdminFarmPlot.fromJson(Map<String, dynamic> json) => AdminFarmPlot(
    id: (json['id'] as num).toInt(),
    name: json['name'] as String,
    areaSqm: (json['area_sqm'] as num).toDouble(),
    status: json['status'] as String,
    provinceId: (json['province_id'] as num?)?.toInt(),
    cityId: (json['city_id'] as num?)?.toInt(),
    cyclesCount: (json['cycles_count'] as num).toInt(),
  );
}

class AdminFarmCycle {
  const AdminFarmCycle({
    required this.id,
    required this.plotId,
    required this.cropId,
    required this.status,
    required this.plannedStartDate,
    this.varietyId,
    this.title,
    this.plannedEndDate,
    this.actualStartDate,
    this.actualEndDate,
  });

  final int id;
  final int plotId;
  final int cropId;
  final int? varietyId;
  final String? title;
  final String status;
  final String plannedStartDate;
  final String? plannedEndDate;
  final String? actualStartDate;
  final String? actualEndDate;

  factory AdminFarmCycle.fromJson(Map<String, dynamic> json) => AdminFarmCycle(
    id: (json['id'] as num).toInt(),
    plotId: (json['plot_id'] as num).toInt(),
    cropId: (json['crop_id'] as num).toInt(),
    varietyId: (json['variety_id'] as num?)?.toInt(),
    title: json['title'] as String?,
    status: json['status'] as String,
    plannedStartDate: json['planned_start_date'] as String,
    plannedEndDate: json['planned_end_date'] as String?,
    actualStartDate: json['actual_start_date'] as String?,
    actualEndDate: json['actual_end_date'] as String?,
  );
}

class AdminFarmDetail {
  const AdminFarmDetail({
    required this.summary,
    required this.plots,
    required this.cycles,
  });

  final AdminFarmSummary summary;
  final List<AdminFarmPlot> plots;
  final List<AdminFarmCycle> cycles;

  factory AdminFarmDetail.fromJson(Map<String, dynamic> json) =>
      AdminFarmDetail(
        summary: AdminFarmSummary.fromJson(json),
        plots:
            (json['plots'] as List)
                .map((e) => AdminFarmPlot.fromJson((e as Map).cast()))
                .toList(),
        cycles:
            (json['cycles'] as List)
                .map((e) => AdminFarmCycle.fromJson((e as Map).cast()))
                .toList(),
      );
}

class AdminFarmAudit {
  const AdminFarmAudit({
    required this.id,
    required this.actorUserId,
    required this.action,
    required this.targetType,
    required this.targetId,
    required this.createdAt,
  });

  final int id;
  final int actorUserId;
  final String action;
  final String targetType;
  final int targetId;
  final String createdAt;

  factory AdminFarmAudit.fromJson(Map<String, dynamic> json) => AdminFarmAudit(
    id: (json['id'] as num).toInt(),
    actorUserId: (json['actor_user_id'] as num).toInt(),
    action: json['action'] as String,
    targetType: json['target_type'] as String,
    targetId: (json['target_id'] as num).toInt(),
    createdAt: json['created_at'] as String,
  );
}

class AdminFarmPage {
  const AdminFarmPage({
    required this.items,
    required this.page,
    required this.total,
    required this.totalPages,
  });

  final List<AdminFarmSummary> items;
  final int page;
  final int total;
  final int totalPages;
}
