import '../domain/farm_calculators.dart';

class FarmToolCalculationModel {
  const FarmToolCalculationModel({
    required this.id,
    required this.farmId,
    required this.type,
    required this.formulaVersion,
    required this.title,
    required this.inputValues,
    required this.inputUnits,
    required this.resultValues,
    required this.resultUnits,
    required this.createdAt,
    this.plotId,
    this.cycleId,
    this.notes,
  });

  final int id;
  final int farmId;
  final int? plotId;
  final int? cycleId;
  final FarmCalculatorType type;
  final String formulaVersion;
  final String title;
  final Map<String, double> inputValues;
  final Map<String, String> inputUnits;
  final Map<String, double> resultValues;
  final Map<String, String> resultUnits;
  final String? notes;
  final DateTime createdAt;

  factory FarmToolCalculationModel.fromJson(Map<String, dynamic> json) =>
      FarmToolCalculationModel(
        id: json['id'] as int,
        farmId: json['farm_id'] as int,
        plotId: json['plot_id'] as int?,
        cycleId: json['cycle_id'] as int?,
        type: FarmCalculatorType.fromApi(json['calculator_type'] as String),
        formulaVersion: json['formula_version'] as String,
        title: json['title'] as String,
        inputValues: _doubleMap(json['input_values']),
        inputUnits: _stringMap(json['input_units']),
        resultValues: _doubleMap(json['result_values']),
        resultUnits: _stringMap(json['result_units']),
        notes: json['notes'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class FarmFinancialEntryModel {
  const FarmFinancialEntryModel({
    required this.id,
    required this.farmId,
    required this.entryType,
    required this.category,
    required this.amountToman,
    required this.occurredOn,
    required this.createdAt,
    this.plotId,
    this.cycleId,
    this.description,
    this.voidedAt,
    this.voidReason,
  });

  final int id;
  final int farmId;
  final int? plotId;
  final int? cycleId;
  final String entryType;
  final String category;
  final double amountToman;
  final DateTime occurredOn;
  final String? description;
  final DateTime? voidedAt;
  final String? voidReason;
  final DateTime createdAt;

  bool get isVoided => voidedAt != null;
  bool get isExpense => entryType == 'expense';

  factory FarmFinancialEntryModel.fromJson(Map<String, dynamic> json) =>
      FarmFinancialEntryModel(
        id: json['id'] as int,
        farmId: json['farm_id'] as int,
        plotId: json['plot_id'] as int?,
        cycleId: json['cycle_id'] as int?,
        entryType: json['entry_type'] as String,
        category: json['category'] as String,
        amountToman: _double(json['amount_toman']),
        occurredOn: DateTime.parse(json['occurred_on'] as String),
        description: json['description'] as String?,
        voidedAt: _date(json['voided_at']),
        voidReason: json['void_reason'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class FarmFinancialSummaryModel {
  const FarmFinancialSummaryModel({
    required this.farmId,
    required this.expenseToman,
    required this.revenueToman,
    required this.netToman,
    required this.activeEntryCount,
    this.plotId,
    this.cycleId,
  });

  final int farmId;
  final int? plotId;
  final int? cycleId;
  final double expenseToman;
  final double revenueToman;
  final double netToman;
  final int activeEntryCount;

  factory FarmFinancialSummaryModel.fromJson(Map<String, dynamic> json) =>
      FarmFinancialSummaryModel(
        farmId: json['farm_id'] as int,
        plotId: json['plot_id'] as int?,
        cycleId: json['cycle_id'] as int?,
        expenseToman: _double(json['expense_toman']),
        revenueToman: _double(json['revenue_toman']),
        netToman: _double(json['net_toman']),
        activeEntryCount: json['active_entry_count'] as int? ?? 0,
      );
}

class FarmPlanModel {
  const FarmPlanModel({
    required this.id,
    required this.farmId,
    required this.operationType,
    required this.title,
    required this.plannedFor,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.plotId,
    this.cycleId,
    this.reminderAt,
    this.reminderSentAt,
    this.notes,
    this.completedAt,
    this.cancelledAt,
    this.cancelReason,
    this.farmOperationId,
  });

  final int id;
  final int farmId;
  final int? plotId;
  final int? cycleId;
  final String operationType;
  final String title;
  final DateTime plannedFor;
  final DateTime? reminderAt;
  final DateTime? reminderSentAt;
  final String status;
  final String? notes;
  final DateTime? completedAt;
  final DateTime? cancelledAt;
  final String? cancelReason;
  final int? farmOperationId;
  final DateTime createdAt;
  final DateTime updatedAt;

  bool get isPlanned => status == 'planned';
  bool get isOverdue => isPlanned && plannedFor.isBefore(_today());

  factory FarmPlanModel.fromJson(Map<String, dynamic> json) => FarmPlanModel(
    id: json['id'] as int,
    farmId: json['farm_id'] as int,
    plotId: json['plot_id'] as int?,
    cycleId: json['cycle_id'] as int?,
    operationType: json['operation_type'] as String,
    title: json['title'] as String,
    plannedFor: DateTime.parse(json['planned_for'] as String),
    reminderAt: _date(json['reminder_at']),
    reminderSentAt: _date(json['reminder_sent_at']),
    status: json['status'] as String,
    notes: json['notes'] as String?,
    completedAt: _date(json['completed_at']),
    cancelledAt: _date(json['cancelled_at']),
    cancelReason: json['cancel_reason'] as String?,
    farmOperationId: json['farm_operation_id'] as int?,
    createdAt: DateTime.parse(json['created_at'] as String),
    updatedAt: DateTime.parse(json['updated_at'] as String),
  );

  static DateTime _today() {
    final now = DateTime.now();
    return DateTime(now.year, now.month, now.day);
  }
}

Map<String, double> _doubleMap(Object? value) => (value as Map? ?? const {})
    .map((key, value) => MapEntry(key.toString(), _double(value)));

Map<String, String> _stringMap(Object? value) => (value as Map? ?? const {})
    .map((key, value) => MapEntry(key.toString(), value.toString()));

double _double(Object? value) => double.tryParse(value.toString()) ?? 0;

DateTime? _date(Object? value) =>
    value == null ? null : DateTime.tryParse(value.toString());
