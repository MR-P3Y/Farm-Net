import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_verification_models.dart';

class AdminVerificationApiException implements Exception {
  const AdminVerificationApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminVerificationApi {
  AdminVerificationApi({
    AdminApiClient? client,
    AdminTokenStorage? tokenStorage,
  }) : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
       _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminVerificationRequest>> listVerifications({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? targetRole,
  }) async {
    await _setStoredToken();

    final query = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };

    if (status != null && status.isNotEmpty) {
      query['status'] = status;
    }

    if (targetRole != null && targetRole.isNotEmpty) {
      query['target_role'] = targetRole;
    }

    final uri = Uri(path: '/admin/verifications', queryParameters: query);
    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => AdminVerificationRequest.fromJson((item as Map).cast()))
        .toList();
  }

  Future<AdminVerificationRequest> getDetail(int requestId) async {
    await _setStoredToken();

    final json = await _get('/admin/verifications/$requestId');
    return AdminVerificationRequest.fromJson((json['data'] as Map).cast());
  }

  Future<AdminVerificationRequest> updateStatus({
    required int requestId,
    required String status,
    String? note,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/verifications/$requestId/status',
      data: {'status': status, 'note': note},
    );

    return AdminVerificationRequest.fromJson((json['data'] as Map).cast());
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
      throw AdminVerificationApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminVerificationApiException(_mapDioError(error));
    }
  }

  AdminApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map) {
      return AdminApiError.fromJson(data.cast<String, dynamic>());
    }

    return AdminApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
