import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_media_models.dart';

class AdminMediaApiException implements Exception {
  const AdminMediaApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminMediaApi {
  AdminMediaApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminMediaFile>> listMedia({
    String? purpose,
    String? visibility,
    String? status,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (purpose != null && purpose.isNotEmpty) query['purpose'] = purpose;
    if (visibility != null && visibility.isNotEmpty) {
      query['visibility'] = visibility;
    }
    if (status != null && status.isNotEmpty) query['status'] = status;

    final uri = Uri(path: '/admin/media', queryParameters: query);

    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        uri.toString(),
      );
      final json = response.data ?? {};
      final rows = json['data'] as List? ?? [];

      return rows
          .map((item) => AdminMediaFile.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (error) {
      throw AdminMediaApiException(_mapDioError(error));
    }
  }

  Future<AdminMediaFile> getMedia(String fileKey) async {
    await _setStoredToken();

    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/admin/media/$fileKey',
      );
      final json = response.data ?? {};

      return AdminMediaFile.fromJson(json['data'] as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AdminMediaApiException(_mapDioError(error));
    }
  }

  Future<AdminMediaFile> updateStatus({
    required String fileKey,
    required String status,
    String? description,
  }) async {
    await _setStoredToken();

    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        '/admin/media/$fileKey/status',
        data: {'status': status, 'description': description},
      );
      final json = response.data ?? {};

      return AdminMediaFile.fromJson(json['data'] as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AdminMediaApiException(_mapDioError(error));
    }
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
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
