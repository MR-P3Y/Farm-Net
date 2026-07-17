import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'notification_models.dart';

class NotificationApiException implements Exception {
  const NotificationApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class NotificationApi {
  NotificationApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<List<NotificationModel>> listMyNotifications({
    String? status,
    String channel = 'in_app',
    int page = 1,
    int pageSize = 20,
  }) async {
    await _setStoredToken();

    final query = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
      'channel': channel,
    };

    if (status != null && status.isNotEmpty) {
      query['status'] = status;
    }

    final uri = Uri(path: '/notifications/me', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => NotificationModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<int> unreadCount() async {
    await _setStoredToken();

    final json = await _get('/notifications/me/unread-count');
    final data = json['data'] as Map<String, dynamic>? ?? {};

    return NotificationUnreadCount.fromJson(data).unreadCount;
  }

  Future<NotificationModel> markRead(int notificationId) async {
    await _setStoredToken();

    final json = await _patch('/notifications/$notificationId/read');
    return NotificationModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<int> markAllRead() async {
    await _setStoredToken();

    final json = await _patch('/notifications/read-all');
    final data = json['data'] as Map<String, dynamic>? ?? {};

    return (data['updated_count'] as num?)?.toInt() ?? 0;
  }

  Future<NotificationModel> deleteNotification(int notificationId) async {
    await _setStoredToken();

    final json = await _delete('/notifications/$notificationId');
    return NotificationModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<NotificationPreferenceModel>> listPreferences() async {
    await _setStoredToken();
    final json = await _get('/notifications/preferences');
    final rows = json['data'] as List? ?? [];
    return rows
        .map(
          (item) => NotificationPreferenceModel.fromJson(
            item as Map<String, dynamic>,
          ),
        )
        .toList();
  }

  Future<NotificationPreferenceModel> setPreference({
    required String eventType,
    required String channel,
    required bool isEnabled,
  }) async {
    await _setStoredToken();
    final json = await _put('/notifications/preferences', {
      'event_type': eventType,
      'channel': channel,
      'is_enabled': isEnabled,
    });
    return NotificationPreferenceModel.fromJson(
      json['data'] as Map<String, dynamic>,
    );
  }

  Future<NotificationDeviceModel> registerDevice({
    required String token,
    required String platform,
  }) async {
    await _setStoredToken();
    final json = await _post('/notifications/devices', {
      'token': token,
      'platform': platform,
    });
    return NotificationDeviceModel.fromJson(
      json['data'] as Map<String, dynamic>,
    );
  }

  Future<void> unregisterDevice(int deviceId) async {
    await _setStoredToken();
    await _delete('/notifications/devices/$deviceId');
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw NotificationApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _patch(String path) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw NotificationApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _delete(String path) async {
    try {
      final response = await _client.dio.delete<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw NotificationApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _put(
    String path,
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.dio.put<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (e) {
      throw NotificationApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (e) {
      throw NotificationApiException(_mapDioError(e));
    }
  }

  ApiError _mapDioError(DioException e) {
    final data = e.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: e.message ?? 'Network error',
      traceId: e.response?.headers.value('x-trace-id'),
    );
  }
}
