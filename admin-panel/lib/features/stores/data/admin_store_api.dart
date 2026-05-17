import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_store_models.dart';

class AdminStoreApiException implements Exception {
  const AdminStoreApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminStoreApi {
  AdminStoreApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminStore>> listStores({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? q,
  }) async {
    await _setStoredToken();

    final query = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };

    if (status != null && status.isNotEmpty) {
      query['status'] = status;
    }

    if (q != null && q.trim().isNotEmpty) {
      query['q'] = q.trim();
    }

    final uri = Uri(path: '/admin/stores', queryParameters: query);
    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => AdminStore.fromJson((item as Map).cast()))
        .toList();
  }

  Future<AdminStore> getStoreDetail(int storeId) async {
    await _setStoredToken();

    final json = await _get('/admin/stores/$storeId');
    return AdminStore.fromJson((json['data'] as Map).cast());
  }

  Future<AdminStore> updateStatus({
    required int storeId,
    required String status,
    String? note,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/stores/$storeId/status',
      data: {'status': status, 'note': note},
    );

    return AdminStore.fromJson((json['data'] as Map).cast());
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
      throw AdminStoreApiException(_mapDioError(error));
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
      throw AdminStoreApiException(_mapDioError(error));
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
