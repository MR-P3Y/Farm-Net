import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_notification_api.dart';
import 'admin_notification_models.dart';

final adminNotificationRepositoryProvider =
    Provider<AdminNotificationRepository>((ref) {
      return AdminNotificationRepository(api: AdminNotificationApi());
    });

class AdminNotificationRepository {
  AdminNotificationRepository({required AdminNotificationApi api}) : _api = api;

  final AdminNotificationApi _api;

  Future<List<AdminNotificationModel>> listNotifications({
    String? status,
    String? channel,
    int? recipientUserId,
  }) {
    return _api.listNotifications(
      status: status,
      channel: channel,
      recipientUserId: recipientUserId,
    );
  }

  Future<AdminNotificationModel> getNotification(int id) {
    return _api.getNotification(id);
  }

  Future<AdminNotificationModel> createSystemMessage({
    required int recipientUserId,
    required String title,
    required String body,
    String? actionUrl,
    String priority = 'normal',
  }) {
    return _api.createSystemMessage(
      recipientUserId: recipientUserId,
      title: title,
      body: body,
      actionUrl: actionUrl,
      priority: priority,
    );
  }

  Future<AdminDeliveryPage> listDeliveries({
    int page = 1,
    String? status,
    String? channel,
  }) => _api.listDeliveries(page: page, status: status, channel: channel);
  Future<AdminDeliveryModel> getDelivery(int id) => _api.getDelivery(id);
  Future<AdminDeliveryModel> retryDelivery(int id) => _api.retryDelivery(id);
}
