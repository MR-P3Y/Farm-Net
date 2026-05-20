import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_commission_models.dart';

class AdminCommissionApiException implements Exception {
  const AdminCommissionApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminCommissionApi {
  AdminCommissionApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminCommissionSetting>> listSettings() async {
    await _setStoredToken();

    final json = await _get('/admin/commission/settings');
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => AdminCommissionSetting.fromJson((item as Map).cast()))
        .toList();
  }

  Future<AdminCommissionSetting> getDefault() async {
    await _setStoredToken();

    final json = await _get('/admin/commission/settings/default');
    return AdminCommissionSetting.fromJson((json['data'] as Map).cast());
  }

  Future<AdminCommissionSetting> updateDefault({
    required num percent,
    String? description,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/commission/settings/default',
      data: {'percent': percent, 'description': description},
    );

    return AdminCommissionSetting.fromJson((json['data'] as Map).cast());
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
      throw AdminCommissionApiException(_mapDioError(error));
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
      throw AdminCommissionApiException(_mapDioError(error));
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
