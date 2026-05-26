import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_weather_models.dart';

class AdminWeatherApiException implements Exception {
  const AdminWeatherApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminWeatherApi {
  AdminWeatherApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminWeatherProviderConfig>> listProviderConfigs() async {
    await _setStoredToken();

    final json = await _get('/admin/weather/provider-configs');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) =>
              AdminWeatherProviderConfig.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminWeatherProviderConfig> updateProviderConfig({
    required int id,
    required bool isActive,
    required int priority,
    String? baseUrl,
    String? apiKeyRef,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/weather/provider-configs/$id',
      data: {
        'is_active': isActive,
        'priority': priority,
        'base_url': baseUrl,
        'api_key_ref': apiKeyRef,
      },
    );

    return AdminWeatherProviderConfig.fromJson(
      json['data'] as Map<String, dynamic>,
    );
  }

  Future<List<AdminWeatherLocation>> listLocations() async {
    await _setStoredToken();

    final json = await _get('/admin/weather/locations?page=1&page_size=50');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => AdminWeatherLocation.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminWeatherCacheStatus> cacheStatus(int locationId) async {
    await _setStoredToken();

    final json = await _get(
      '/admin/weather/locations/$locationId/cache-status',
    );

    return AdminWeatherCacheStatus.fromJson(
      json['data'] as Map<String, dynamic>,
    );
  }

  Future<void> refresh({
    required int locationId,
    String provider = 'mock',
    bool force = true,
  }) async {
    await _setStoredToken();

    await _post(
      '/admin/weather/refresh?location_id=$locationId&provider=$provider&force=$force',
    );
  }

  Future<List<AdminWeatherAlertRule>> listAlertRules() async {
    await _setStoredToken();

    final json = await _get('/admin/weather/alert-rules');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) =>
              AdminWeatherAlertRule.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<List<AdminWeatherAlertRule>> seedAlertRules() async {
    await _setStoredToken();

    final json = await _post('/admin/weather/alert-rules/seed');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) =>
              AdminWeatherAlertRule.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<List<AdminWeatherAlert>> listAlerts({int? locationId}) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (locationId != null) {
      query['location_id'] = locationId.toString();
    }

    final uri = Uri(path: '/admin/weather/alerts', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => AdminWeatherAlert.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AdminWeatherAlertEvaluation> evaluateAlerts({
    required int locationId,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/admin/weather/alerts/evaluate?location_id=$locationId',
    );

    return AdminWeatherAlertEvaluation.fromJson(
      json['data'] as Map<String, dynamic>,
    );
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminWeatherApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminWeatherApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminWeatherApiException(_mapDioError(error));
    }
  }

  AdminApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map<String, dynamic>) {
      return AdminApiError.fromJson(data);
    }

    return AdminApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
