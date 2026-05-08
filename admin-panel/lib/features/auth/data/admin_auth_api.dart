import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import 'admin_auth_models.dart';

class AdminAuthApiException implements Exception {
  const AdminAuthApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminAuthApi {
  AdminAuthApi({AdminApiClient? client})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl);

  final AdminApiClient _client;

  void setToken(String? token) {
    _client.setToken(token);
  }

  Future<AdminTokenPair> loginWithEmail({
    required String email,
    required String password,
  }) async {
    final json = await _post(
      '/auth/login/email',
      data: {'email': email, 'password': password},
    );

    return AdminTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminAuthUser> me() async {
    final json = await _get('/auth/me');

    return AdminAuthUser.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminTokenPair> refresh({required String refreshToken}) async {
    final json = await _post(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );

    return AdminTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<void> logout({required String? refreshToken}) async {
    await _post('/auth/logout', data: {'refresh_token': refreshToken});
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminAuthApiException(_mapDioError(error));
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
      throw AdminAuthApiException(_mapDioError(error));
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
