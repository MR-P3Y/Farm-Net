import '../data/notification_models.dart';

class NotificationState {
  const NotificationState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.unreadCount = 0,
    this.statusFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<NotificationModel> items;
  final int unreadCount;
  final String? statusFilter;
  final String? errorMessage;

  factory NotificationState.initial() {
    return const NotificationState(isLoading: true);
  }

  NotificationState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<NotificationModel>? items,
    int? unreadCount,
    String? statusFilter,
    String? errorMessage,
    bool clearStatusFilter = false,
    bool clearError = false,
  }) {
    return NotificationState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      unreadCount: unreadCount ?? this.unreadCount,
      statusFilter:
          clearStatusFilter ? null : statusFilter ?? this.statusFilter,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
