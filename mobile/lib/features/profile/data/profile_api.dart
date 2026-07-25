import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'profile_models.dart';

class ProfileApiException implements Exception {
  const ProfileApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class ProfileApi {
  ProfileApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<UserProfile> getMe() async {
    await _auth();
    try {
      final response = await _client.get('profiles/me');
      return UserProfile.fromJson(response.data?['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ProfileApiException(_error(e));
    }
  }

  Future<UserProfile> updateMe(ProfileUpdateInput input) async {
    await _auth();
    try {
      final response = await _client.patch('profiles/me', data: input.toJson());
      return UserProfile.fromJson(response.data?['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ProfileApiException(_error(e));
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) return ApiError.fromJson(data);
    return ApiError(code: 'NETWORK_ERROR', message: error.message ?? 'خطا در عملیات پروفایل');
  }
}
