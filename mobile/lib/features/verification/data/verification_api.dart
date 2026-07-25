import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'verification_models.dart';

class VerificationApiException implements Exception {
  const VerificationApiException(this.error);
  final ApiError error;
  @override
  String toString() => '${error.code}: ${error.message}';
}

class VerificationApi {
  VerificationApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<VerificationRequest>> listMine() async {
    final json = await _get('verifications/me');
    final data = json['data'] as List? ?? [];
    return data.map((item) => VerificationRequest.fromJson((item as Map).cast())).toList();
  }

  Future<VerificationRequest> create(VerificationCreateInput input) async {
    final json = await _post('verifications', data: input.toJson());
    return VerificationRequest.fromJson((json['data'] as Map).cast());
  }

  Future<VerificationRequest> attachDocument({
    required int requestId,
    required int documentId,
  }) async {
    final json = await _post(
      'verifications/$requestId/documents',
      data: {'document_id': documentId},
    );
    return VerificationRequest.fromJson((json['data'] as Map).cast());
  }

  Future<VerificationRequest> submit({required int requestId}) async {
    final json = await _post('verifications/$requestId/submit', data: {});
    return VerificationRequest.fromJson((json['data'] as Map).cast());
  }

  Future<Map<String, dynamic>> _get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _client.get(path, queryParameters: queryParameters);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw VerificationApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.post(path, data: data);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw VerificationApiException(_mapDioError(error));
    }
  }

  ApiError _mapDioError(DioException error) {
    final data = error.response?.data;
    if (data is Map) return ApiError.fromJson(data.cast<String, dynamic>());
    return ApiError(code: 'NETWORK_ERROR', message: error.message ?? 'Network error');
  }
}
