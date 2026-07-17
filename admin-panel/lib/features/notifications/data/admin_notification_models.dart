class AdminNotificationModel {
  const AdminNotificationModel({
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

  factory AdminNotificationModel.fromJson(Map<String, dynamic> json) {
    return AdminNotificationModel(
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

class AdminDeliveryAttemptModel {
  const AdminDeliveryAttemptModel({
    required this.attemptNumber,
    required this.status,
    required this.startedAt,
    this.provider,
    this.errorCode,
    this.errorMessage,
    this.finishedAt,
  });
  final int attemptNumber;
  final String status;
  final String startedAt;
  final String? provider;
  final String? errorCode;
  final String? errorMessage;
  final String? finishedAt;
  factory AdminDeliveryAttemptModel.fromJson(Map<String, dynamic> json) =>
      AdminDeliveryAttemptModel(
        attemptNumber: (json['attempt_number'] as num).toInt(),
        status: json['status']?.toString() ?? '',
        startedAt: json['started_at']?.toString() ?? '',
        provider: json['provider']?.toString(),
        errorCode: json['error_code']?.toString(),
        errorMessage: json['error_message']?.toString(),
        finishedAt: json['finished_at']?.toString(),
      );
}

class AdminDeliveryModel {
  const AdminDeliveryModel({
    required this.id,
    required this.notificationId,
    required this.channel,
    required this.status,
    required this.attemptCount,
    required this.maxAttempts,
    required this.createdAt,
    this.provider,
    this.errorCode,
    this.errorMessage,
    this.nextAttemptAt,
    this.attempts = const [],
  });
  final int id;
  final int notificationId;
  final String channel;
  final String status;
  final int attemptCount;
  final int maxAttempts;
  final String createdAt;
  final String? provider;
  final String? errorCode;
  final String? errorMessage;
  final String? nextAttemptAt;
  final List<AdminDeliveryAttemptModel> attempts;
  bool get canRetry =>
      channel != 'in_app' &&
      !{'processing', 'sent', 'delivered'}.contains(status);
  factory AdminDeliveryModel.fromJson(Map<String, dynamic> json) =>
      AdminDeliveryModel(
        id: (json['id'] as num).toInt(),
        notificationId: (json['notification_id'] as num).toInt(),
        channel: json['channel']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
        attemptCount: (json['attempt_count'] as num?)?.toInt() ?? 0,
        maxAttempts: (json['max_attempts'] as num?)?.toInt() ?? 0,
        createdAt: json['created_at']?.toString() ?? '',
        provider: json['provider']?.toString(),
        errorCode: json['error_code']?.toString(),
        errorMessage: json['error_message']?.toString(),
        nextAttemptAt: json['next_attempt_at']?.toString(),
        attempts:
            (json['attempts'] as List? ?? [])
                .map(
                  (item) => AdminDeliveryAttemptModel.fromJson(
                    item as Map<String, dynamic>,
                  ),
                )
                .toList(),
      );
}

class AdminDeliveryPage {
  const AdminDeliveryPage({
    required this.items,
    required this.page,
    required this.totalPages,
  });
  final List<AdminDeliveryModel> items;
  final int page;
  final int totalPages;
}
