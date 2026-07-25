import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'farm_models.dart';

class FarmApiException implements Exception {
  const FarmApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class FarmApi {
  FarmApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<List<FarmModel>> farms() async => _list('/farms', FarmModel.fromJson);

  Future<FarmModel> createFarm(Map<String, dynamic> payload) async =>
      FarmModel.fromJson(await _write('/farms', payload));

  Future<List<FarmPlotModel>> plots(int farmId) async =>
      _list('/farms/$farmId/plots', FarmPlotModel.fromJson);

  Future<FarmPlotModel> createPlot(
    int farmId,
    Map<String, dynamic> payload,
  ) async =>
      FarmPlotModel.fromJson(await _write('/farms/$farmId/plots', payload));

  Future<List<CropReference>> crops() async =>
      _list('/farm-references/crops', CropReference.fromJson);

  Future<List<MeasurementUnitModel>> harvestUnits() async {
    final mass = await _list(
      '/farm-references/measurement-units?dimension=mass',
      MeasurementUnitModel.fromJson,
    );
    final count = await _list(
      '/farm-references/measurement-units?dimension=count',
      MeasurementUnitModel.fromJson,
    );
    return [...mass, ...count];
  }

  Future<List<CropCycleModel>> cycles(int farmId, int plotId) async =>
      _list('/farms/$farmId/plots/$plotId/cycles', CropCycleModel.fromJson);

  Future<CropCycleModel> createCycle(
    int farmId,
    int plotId,
    Map<String, dynamic> payload,
  ) async => CropCycleModel.fromJson(
    await _write('/farms/$farmId/plots/$plotId/cycles', payload),
  );

  Future<CropCycleModel> transitionCycle(
    int farmId,
    int plotId,
    int cycleId,
    String action,
  ) async => CropCycleModel.fromJson(
    await _write('/farms/$farmId/plots/$plotId/cycles/$cycleId/$action', {
      'effective_date': _today(),
    }),
  );

  Future<List<FarmOperationModel>> operations(
    int farmId,
    int plotId,
    int cycleId,
  ) async => _list(
    '/farms/$farmId/plots/$plotId/cycles/$cycleId/operations',
    FarmOperationModel.fromJson,
  );

  Future<void> createOperation(
    int farmId,
    int plotId,
    int cycleId,
    Map<String, dynamic> payload,
  ) async {
    await _write(
      '/farms/$farmId/plots/$plotId/cycles/$cycleId/operations',
      payload,
    );
  }

  Future<List<FarmHarvestModel>> harvests(
    int farmId,
    int plotId,
    int cycleId,
  ) async => _list(
    '/farms/$farmId/plots/$plotId/cycles/$cycleId/harvests',
    FarmHarvestModel.fromJson,
  );

  Future<void> createHarvest(
    int farmId,
    int plotId,
    int cycleId,
    Map<String, dynamic> payload,
  ) async {
    await _write(
      '/farms/$farmId/plots/$plotId/cycles/$cycleId/harvests',
      payload,
    );
  }

  Future<FarmWeatherModel> weather(
    int farmId,
    int plotId, {
    bool refresh = false,
  }) async {
    await _auth();
    final path =
        '/farms/$farmId/plots/$plotId/weather${refresh ? '/refresh' : ''}';
    try {
      final response =
          refresh
              ? await _client.dio.post<Map<String, dynamic>>(path)
              : await _client.dio.get<Map<String, dynamic>>(path);
      return FarmWeatherModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<List<T>> _list<T>(
    String path,
    T Function(Map<String, dynamic>) parse,
  ) async {
    await _auth();
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(parse)
          .toList();
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<Map<String, dynamic>> _write(
    String path,
    Map<String, dynamic> payload,
  ) async {
    await _auth();
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: payload,
      );
      return response.data?['data'] as Map<String, dynamic>;
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) return ApiError.fromJson(data);
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'خطا در ارتباط با سرور',
    );
  }

  String _today() {
    final now = DateTime.now();
    return '${now.year.toString().padLeft(4, '0')}-'
        '${now.month.toString().padLeft(2, '0')}-'
        '${now.day.toString().padLeft(2, '0')}';
  }
}
