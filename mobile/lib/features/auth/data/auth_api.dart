import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'auth_models.dart';

class AuthApiException implements Exception {
  const AuthApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AuthApi {
  AuthApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  void setToken(String? token) {
    _client.setToken(token);
  }

  Future<AuthTokenPair> registerWithEmail({
    required String email,
    required String password,
  }) async {
    final json = await _post(
      '/auth/register/email',
      data: {'email': email, 'password': password},
    );

    return AuthTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AuthTokenPair> loginWithEmail({
    required String email,
    required String password,
  }) async {
    final json = await _post(
      '/auth/login/email',
      data: {'email': email, 'password': password},
    );

    return AuthTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<OtpRequestResult> requestOtp({
    required String phone,
    String purpose = 'login',
  }) async {
    final json = await _post(
      '/auth/otp/request',
      data: {'phone': phone, 'purpose': purpose},
    );

    return OtpRequestResult.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AuthTokenPair> verifyOtp({
    required String phone,
    required String code,
    String purpose = 'login',
  }) async {
    final json = await _post(
      '/auth/otp/verify',
      data: {'phone': phone, 'code': code, 'purpose': purpose},
    );

    return AuthTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AuthUser> me() async {
    final json = await _get('/auth/me');

    return AuthUser.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AuthTokenPair> refresh({required String refreshToken}) async {
    final json = await _post(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );

    return AuthTokenPair.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<void> logout({required String? refreshToken}) async {
    await _post('/auth/logout', data: {'refresh_token': refreshToken});
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw AuthApiException(_mapDioError(error));
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
      throw AuthApiException(_mapDioError(error));
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
