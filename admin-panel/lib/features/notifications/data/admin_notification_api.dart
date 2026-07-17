import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_notification_models.dart';

class AdminNotificationApiException implements Exception {
  const AdminNotificationApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminNotificationApi {
  AdminNotificationApi({
    AdminApiClient? client,
    AdminTokenStorage? tokenStorage,
  }) : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
       _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminNotificationModel>> listNotifications({
    String? status,
    String? channel,
    int? recipientUserId,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (channel != null && channel.isNotEmpty) query['channel'] = channel;
    if (recipientUserId != null) {
      query['recipient_user_id'] = recipientUserId.toString();
    }

    final uri = Uri(path: '/admin/notifications', queryParameters: query);

    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        uri.toString(),
      );
      final json = response.data ?? {};
      final rows = json['data'] as List? ?? [];

      return rows
          .map(
            (item) =>
                AdminNotificationModel.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
    }
  }

  Future<AdminNotificationModel> getNotification(int id) async {
    await _setStoredToken();

    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/admin/notifications/$id',
      );
      final json = response.data ?? {};

      return AdminNotificationModel.fromJson(
        json['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
    }
  }

  Future<AdminNotificationModel> createSystemMessage({
    required int recipientUserId,
    required String title,
    required String body,
    String? actionUrl,
    String priority = 'normal',
  }) async {
    await _setStoredToken();

    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/admin/notifications/system-message',
        data: {
          'recipient_user_id': recipientUserId,
          'title': title,
          'body': body,
          'action_url': actionUrl,
          'priority': priority,
        },
      );
      final json = response.data ?? {};

      return AdminNotificationModel.fromJson(
        json['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
    }
  }

  Future<AdminDeliveryPage> listDeliveries({
    int page = 1,
    String? status,
    String? channel,
  }) async {
    await _setStoredToken();
    final query = <String, String>{'page': '$page', 'page_size': '20'};
    if (status != null) query['status'] = status;
    if (channel != null) query['channel'] = channel;
    final uri = Uri(
      path: '/admin/notifications/deliveries',
      queryParameters: query,
    );
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        uri.toString(),
      );
      final json = response.data ?? {};
      final meta = json['meta'] as Map<String, dynamic>? ?? {};
      return AdminDeliveryPage(
        items:
            (json['data'] as List? ?? [])
                .map(
                  (item) =>
                      AdminDeliveryModel.fromJson(item as Map<String, dynamic>),
                )
                .toList(),
        page: (meta['page'] as num?)?.toInt() ?? page,
        totalPages: (meta['total_pages'] as num?)?.toInt() ?? 0,
      );
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
    }
  }

  Future<AdminDeliveryModel> getDelivery(int id) async {
    await _setStoredToken();
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/admin/notifications/deliveries/$id',
      );
      return AdminDeliveryModel.fromJson(
        (response.data ?? {})['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
    }
  }

  Future<AdminDeliveryModel> retryDelivery(int id) async {
    await _setStoredToken();
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/admin/notifications/deliveries/$id/retry',
      );
      return AdminDeliveryModel.fromJson(
        (response.data ?? {})['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw AdminNotificationApiException(_mapDioError(error));
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
