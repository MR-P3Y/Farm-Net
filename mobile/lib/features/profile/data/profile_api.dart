import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'profile_models.dart';

class ProfileApiException implements Exception {
  const ProfileApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class ProfileApi {
  ProfileApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<UserProfile> getMe() async {
    final json = await _get('/profile/me');
    return UserProfile.fromJson((json['data'] as Map).cast());
  }

  Future<UserProfile> updateMe(ProfileUpdateInput input) async {
    final json = await _put('/profile/me', data: input.toJson());
    return UserProfile.fromJson((json['data'] as Map).cast());
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw ProfileApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _put(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.put<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw ProfileApiException(_mapDioError(error));
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
