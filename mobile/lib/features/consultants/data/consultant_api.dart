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
