class NotificationModel {
  const NotificationModel({
    required this.id,
    required this.recipientUserId,
    required this.channel,
    required this.title,
    required this.body,
    required this.priority,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.eventId,
    this.actionUrl,
    this.readAt,
    this.deletedAt,
  });

  final int id;
  final int? eventId;
  final int recipientUserId;

  final String channel;
  final String title;
  final String body;
  final String? actionUrl;

  final String priority;
  final String status;

  final String? readAt;
  final String createdAt;
  final String updatedAt;
  final String? deletedAt;

  bool get isUnread => status == 'unread';
  bool get isRead => status == 'read';
  bool get isHighPriority => priority == 'high' || priority == 'urgent';

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: (json['id'] as num).toInt(),
      eventId:
          json['event_id'] == null ? null : (json['event_id'] as num).toInt(),
      recipientUserId: (json['recipient_user_id'] as num).toInt(),
      channel: json['channel']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      body: json['body']?.toString() ?? '',
      actionUrl: json['action_url']?.toString(),
      priority: json['priority']?.toString() ?? 'normal',
      status: json['status']?.toString() ?? 'unread',
      readAt: json['read_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      deletedAt: json['deleted_at']?.toString(),
    );
  }
}

class NotificationUnreadCount {
  const NotificationUnreadCount({required this.unreadCount});

  final int unreadCount;

  factory NotificationUnreadCount.fromJson(Map<String, dynamic> json) {
    return NotificationUnreadCount(
      unreadCount: (json['unread_count'] as num?)?.toInt() ?? 0,
    );
  }
}

class NotificationPreferenceModel {
  const NotificationPreferenceModel({
    required this.id,
    required this.eventType,
    required this.channel,
    required this.isEnabled,
  });
  final int id;
  final String eventType;
  final String channel;
  final bool isEnabled;

  factory NotificationPreferenceModel.fromJson(Map<String, dynamic> json) {
    return NotificationPreferenceModel(
      id: (json['id'] as num).toInt(),
      eventType: json['event_type']?.toString() ?? '*',
      channel: json['channel']?.toString() ?? 'in_app',
      isEnabled: json['is_enabled'] == true,
    );
  }
}

class NotificationDeviceModel {
  const NotificationDeviceModel({
    required this.id,
    required this.platform,
    required this.isActive,
  });
  final int id;
  final String platform;
  final bool isActive;

  factory NotificationDeviceModel.fromJson(Map<String, dynamic> json) {
    return NotificationDeviceModel(
      id: (json['id'] as num).toInt(),
      platform: json['platform']?.toString() ?? '',
      isActive: json['is_active'] == true,
    );
  }
}
