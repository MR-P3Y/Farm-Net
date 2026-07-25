import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'geo_models.dart';

class GeoApiException implements Exception {
  const GeoApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class GeoApi {
  GeoApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<GeoProvince>> getProvinces() async {
    final json = await _get('geo/provinces');
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => GeoProvince.fromJson((item as Map).cast()))
        .toList();
  }

  Future<List<GeoCounty>> getCounties({required int provinceId}) async {
    final json = await _get('geo/counties', queryParameters: {'province_id': provinceId});
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => GeoCounty.fromJson((item as Map).cast()))
        .toList();
  }

  Future<List<GeoCity>> getCities({
    int? provinceId,
    int? countyId,
    String? q,
  }) async {
    final query = <String, dynamic>{};

    if (provinceId != null) query['province_id'] = provinceId;
    if (countyId != null) query['county_id'] = countyId;
    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();

    final json = await _get('geo/cities', queryParameters: query);
    final data = json['data'] as List? ?? [];

    return data.map((item) => GeoCity.fromJson((item as Map).cast())).toList();
  }

  Future<Map<String, dynamic>> _get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _client.get(path, queryParameters: queryParameters);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw GeoApiException(_mapDioError(error));
    }
  }

  ApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map) {
      return ApiError.fromJson(data.cast<String, dynamic>());
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
