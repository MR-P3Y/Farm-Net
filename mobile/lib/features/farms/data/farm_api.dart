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

  Future<List<FarmModel>> farms({bool includeArchived = false}) async => _list(
    'farms',
    FarmModel.fromJson,
    queryParameters: {'include_archived': includeArchived},
  );

  Future<FarmModel> farm(int farmId) async =>
      FarmModel.fromJson(await _read('farms/$farmId'));

  Future<FarmModel> createFarm(Map<String, dynamic> payload) async =>
      FarmModel.fromJson(await _write('farms', payload));

  Future<FarmModel> updateFarm(
    int farmId,
    Map<String, dynamic> payload,
  ) async => FarmModel.fromJson(await _patch('farms/$farmId', payload));

  Future<FarmModel> archiveFarm(int farmId, {String? reason}) async =>
      FarmModel.fromJson(
        await _write('farms/$farmId/archive', {'reason': reason}),
      );

  Future<FarmModel> restoreFarm(int farmId) async =>
      FarmModel.fromJson(await _write('farms/$farmId/restore', const {}));

  Future<List<FarmPlotModel>> plots(int farmId) async =>
      _list('farms/$farmId/plots', FarmPlotModel.fromJson);

  Future<FarmPlotModel> createPlot(
    int farmId,
    Map<String, dynamic> payload,
  ) async =>
      FarmPlotModel.fromJson(await _write('farms/$farmId/plots', payload));

  Future<List<CropReference>> crops() async =>
      _list('farm-references/crops', CropReference.fromJson);

  Future<List<MeasurementUnitModel>> harvestUnits() async {
    final mass = await _list(
      'farm-references/measurement-units',
      MeasurementUnitModel.fromJson,
      queryParameters: {'dimension': 'mass'},
    );
    final count = await _list(
      'farm-references/measurement-units',
      MeasurementUnitModel.fromJson,
      queryParameters: {'dimension': 'count'},
    );
    return [...mass, ...count];
  }

  Future<List<CropCycleModel>> cycles(int farmId, int plotId) async =>
      _list('farms/$farmId/plots/$plotId/cycles', CropCycleModel.fromJson);

  Future<CropCycleModel> createCycle(
    int farmId,
    int plotId,
    Map<String, dynamic> payload,
  ) async => CropCycleModel.fromJson(
    await _write('farms/$farmId/plots/$plotId/cycles', payload),
  );

  Future<CropCycleModel> transitionCycle(
    int farmId,
    int plotId,
    int cycleId,
    String action,
  ) async => CropCycleModel.fromJson(
    await _write('farms/$farmId/plots/$plotId/cycles/$cycleId/$action', {
      'effective_date': _today(),
    }),
  );

  Future<List<FarmOperationModel>> operations(
    int farmId,
    int plotId,
    int cycleId,
  ) async => _list(
    'farms/$farmId/plots/$plotId/cycles/$cycleId/operations',
    FarmOperationModel.fromJson,
  );

  Future<void> createOperation(
    int farmId,
    int plotId,
    int cycleId,
    Map<String, dynamic> payload,
  ) async {
    await _write(
      'farms/$farmId/plots/$plotId/cycles/$cycleId/operations',
      payload,
    );
  }

  Future<List<FarmHarvestModel>> harvests(
    int farmId,
    int plotId,
    int cycleId,
  ) async => _list(
    'farms/$farmId/plots/$plotId/cycles/$cycleId/harvests',
    FarmHarvestModel.fromJson,
  );

  Future<void> createHarvest(
    int farmId,
    int plotId,
    int cycleId,
    Map<String, dynamic> payload,
  ) async {
    await _write(
      'farms/$farmId/plots/$plotId/cycles/$cycleId/harvests',
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
        'farms/$farmId/plots/$plotId/weather${refresh ? '/refresh' : ''}';
    try {
      final response =
          refresh ? await _client.post(path) : await _client.get(path);
      return FarmWeatherModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<List<T>> _list<T>(
    String path,
    T Function(Map<String, dynamic>) parse, {
    Map<String, dynamic>? queryParameters,
  }) async {
    await _auth();
    try {
      final response = await _client.get(
        path,
        queryParameters: queryParameters,
      );
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
      final response = await _client.post(path, data: payload);
      return response.data?['data'] as Map<String, dynamic>;
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<Map<String, dynamic>> _read(String path) async {
    await _auth();
    try {
      final response = await _client.get(path);
      return response.data?['data'] as Map<String, dynamic>;
    } on DioException catch (error) {
      throw FarmApiException(_error(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path,
    Map<String, dynamic> payload,
  ) async {
    await _auth();
    try {
      final response = await _client.patch(path, data: payload);
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
