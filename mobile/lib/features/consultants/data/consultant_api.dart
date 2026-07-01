import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'consultant_models.dart';

class ConsultantApiException implements Exception {
  const ConsultantApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class ConsultantApi {
  ConsultantApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<ConsultantSpecialtyModel>> specialties() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/specialties',
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultantSpecialtyModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<List<ConsultantProfileModel>> list({
    int? specialtyId,
    String? query,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final params = <String, dynamic>{'page': page, 'page_size': pageSize};

      if (specialtyId != null) params['specialty_id'] = specialtyId;
      if (query != null && query.trim().isNotEmpty) {
        params['q'] = query.trim();
      }

      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultantProfileModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel> detail(int profileId) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/$profileId',
      );
      final json = response.data ?? {};

      return ConsultantProfileModel.fromJson(
        json['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
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
