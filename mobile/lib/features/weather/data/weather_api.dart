import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'weather_models.dart';

class WeatherApiException implements Exception {
  const WeatherApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class WeatherApi {
  WeatherApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<List<WeatherLocationModel>> listLocations() async {
    final json = await _get('weather/locations', queryParameters: {'page': 1, 'page_size': 50});
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => WeatherLocationModel.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<WeatherLocationModel> createGpsLocation({
    required double latitude,
    required double longitude,
    String? displayName,
    String? timezone,
  }) async {
    await _setStoredToken();

    final json = await _post(
      'weather/locations/gps',
      data: {
        'latitude': latitude,
        'longitude': longitude,
        'display_name': displayName,
        'timezone': timezone,
      },
    );

    return WeatherLocationModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<WeatherSnapshotModel?> current(int locationId) async {
    final json = await _get('weather/current', queryParameters: {'location_id': locationId});
    final data = json['data'];

    if (data == null) return null;
    if (data is Map && data.isEmpty) return null;

    return WeatherSnapshotModel.fromJson(data as Map<String, dynamic>);
  }

  Future<List<WeatherForecastModel>> forecast(int locationId) async {
    final json = await _get('weather/forecast', queryParameters: {'location_id': locationId});
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => WeatherForecastModel.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<List<WeatherAlertModel>> alerts(int locationId) async {
    final json = await _get('weather/alerts', queryParameters: {'location_id': locationId});
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => WeatherAlertModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> refresh({
    required int locationId,
    String provider = 'mock',
  }) async {
    await _setStoredToken();

    await _post('weather/refresh', queryParameters: {
      'location_id': locationId,
      'provider': provider,
    });
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _client.get(path, queryParameters: queryParameters);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (e) {
      throw WeatherApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    Map<String, dynamic>? data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _client.post(path, data: data, queryParameters: queryParameters);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (e) {
      throw WeatherApiException(_mapDioError(e));
    }
  }

  ApiError _mapDioError(DioException e) {
    final data = e.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: e.message ?? 'Network error',
      traceId: e.response?.headers.value('x-trace-id'),
    );
  }
}
