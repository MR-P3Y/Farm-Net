import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'notification_api.dart';
import 'notification_models.dart';

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(api: NotificationApi());
});

class NotificationRepository {
  NotificationRepository({required NotificationApi api}) : _api = api;

  final NotificationApi _api;

  Future<List<NotificationModel>> listMyNotifications({
    String? status,
    String channel = 'in_app',
    int page = 1,
    int pageSize = 20,
  }) {
    return _api.listMyNotifications(
      status: status,
      channel: channel,
      page: page,
      pageSize: pageSize,
    );
  }

  Future<int> unreadCount() {
    return _api.unreadCount();
  }

  Future<NotificationModel> markRead(int notificationId) {
    return _api.markRead(notificationId);
  }

  Future<int> markAllRead() {
    return _api.markAllRead();
  }

  Future<NotificationModel> deleteNotification(int notificationId) {
    return _api.deleteNotification(notificationId);
  }
}
