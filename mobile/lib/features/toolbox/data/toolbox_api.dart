import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import '../domain/farm_calculators.dart';
import 'toolbox_models.dart';

class ToolboxApiException implements Exception {
  const ToolboxApiException(this.error, {this.statusCode});

  final ApiError error;
  final int? statusCode;

  bool get isNotFound => statusCode == 404;
  bool get isOffline => statusCode == null || error.code == 'NETWORK_ERROR';

  @override
  String toString() => error.message;
}

class ToolboxApi {
  ToolboxApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<FarmToolCalculationModel> saveCalculation({
    required int farmId,
    required FarmCalculatorType type,
    required String title,
    required Map<String, double> inputValues,
    required Map<String, String> inputUnits,
    int? plotId,
    int? cycleId,
    String? notes,
  }) async => FarmToolCalculationModel.fromJson(
    await _post('farms/$farmId/toolbox/calculations', {
      'plot_id': plotId,
      'cycle_id': cycleId,
      'calculator_type': type.apiValue,
      'formula_version': FarmCalculatorEngine.formulaVersion,
      'title': title,
      'input_values': inputValues,
      'input_units': inputUnits,
      'notes': notes,
    }),
  );

  Future<List<FarmToolCalculationModel>> calculations({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _list(
    'farms/$farmId/toolbox/calculations',
    FarmToolCalculationModel.fromJson,
    query: {'plot_id': plotId, 'cycle_id': cycleId, 'limit': 100},
  );

  Future<FarmFinancialEntryModel> createCost({
    required int farmId,
    required Map<String, dynamic> payload,
  }) async => FarmFinancialEntryModel.fromJson(
    await _post('farms/$farmId/toolbox/costs', payload),
  );

  Future<List<FarmFinancialEntryModel>> costs({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _list(
    'farms/$farmId/toolbox/costs',
    FarmFinancialEntryModel.fromJson,
    query: {'plot_id': plotId, 'cycle_id': cycleId, 'limit': 200},
  );

  Future<FarmFinancialSummaryModel> costSummary({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) async => FarmFinancialSummaryModel.fromJson(
    await _get('farms/$farmId/toolbox/cost-summary', {
      'plot_id': plotId,
      'cycle_id': cycleId,
    }),
  );

  Future<FarmFinancialEntryModel> voidCost({
    required int farmId,
    required int entryId,
    required String reason,
  }) async => FarmFinancialEntryModel.fromJson(
    await _post('farms/$farmId/toolbox/costs/$entryId/void', {
      'reason': reason,
    }),
  );

  Future<FarmPlanModel> createPlan({
    required int farmId,
    required Map<String, dynamic> payload,
  }) async => FarmPlanModel.fromJson(
    await _post('farms/$farmId/toolbox/plans', payload),
  );

  Future<List<FarmPlanModel>> plans({
    required int farmId,
    int? plotId,
    int? cycleId,
  }) => _list(
    'farms/$farmId/toolbox/plans',
    FarmPlanModel.fromJson,
    query: {'plot_id': plotId, 'cycle_id': cycleId, 'limit': 200},
  );

  Future<FarmPlanModel> completePlan({
    required int farmId,
    required int planId,
    required bool writeToDiary,
  }) async => FarmPlanModel.fromJson(
    await _post('farms/$farmId/toolbox/plans/$planId/complete', {
      'occurred_on': _today(),
      'write_to_diary': writeToDiary,
    }),
  );

  Future<FarmPlanModel> cancelPlan({
    required int farmId,
    required int planId,
    String? reason,
  }) async => FarmPlanModel.fromJson(
    await _post('farms/$farmId/toolbox/plans/$planId/cancel', {
      'reason': reason,
    }),
  );

  Future<List<T>> _list<T>(
    String path,
    T Function(Map<String, dynamic>) parse, {
    Map<String, dynamic>? query,
  }) async {
    await _auth();
    try {
      final response = await _client.get(
        path,
        queryParameters: _withoutNulls(query),
      );
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(parse)
          .toList(growable: false);
    } on DioException catch (error) {
      throw ToolboxApiException(
        _error(error),
        statusCode: error.response?.statusCode,
      );
    }
  }

  Future<Map<String, dynamic>> _get(
    String path,
    Map<String, dynamic>? query,
  ) async {
    await _auth();
    try {
      final response = await _client.get(
        path,
        queryParameters: _withoutNulls(query),
      );
      return response.data?['data'] as Map<String, dynamic>;
    } on DioException catch (error) {
      throw ToolboxApiException(
        _error(error),
        statusCode: error.response?.statusCode,
      );
    }
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> payload,
  ) async {
    await _auth();
    try {
      final response = await _client.post(path, data: payload);
      return response.data?['data'] as Map<String, dynamic>;
    } on DioException catch (error) {
      throw ToolboxApiException(
        _error(error),
        statusCode: error.response?.statusCode,
      );
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      if (data['error'] is Map) return ApiError.fromJson(data);
      return ApiError(
        code: error.response?.statusCode == 404 ? 'NOT_FOUND' : 'HTTP_ERROR',
        message: data['detail']?.toString() ?? 'خطای پاسخ سرور',
      );
    }
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'خطا در ارتباط با سرور',
    );
  }

  Map<String, dynamic>? _withoutNulls(Map<String, dynamic>? value) {
    if (value == null) return null;
    return Map.fromEntries(value.entries.where((entry) => entry.value != null));
  }

  String _today() {
    final now = DateTime.now();
    return '${now.year.toString().padLeft(4, '0')}-'
        '${now.month.toString().padLeft(2, '0')}-'
        '${now.day.toString().padLeft(2, '0')}';
  }
}
