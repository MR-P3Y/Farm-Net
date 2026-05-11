import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'document_models.dart';

class DocumentApiException implements Exception {
  const DocumentApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class DocumentApi {
  DocumentApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<UserDocument>> listMyDocuments() async {
    final json = await _get('/documents/me');
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => UserDocument.fromJson((item as Map).cast()))
        .toList();
  }

  Future<UserDocument> createDocument(DocumentCreateInput input) async {
    final json = await _post('/documents', data: input.toJson());
    return UserDocument.fromJson((json['data'] as Map).cast());
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw DocumentApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw DocumentApiException(_mapDioError(error));
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
