import '../data/admin_notification_models.dart';

class AdminNotificationState {
  const AdminNotificationState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.selected,
    this.statusFilter,
    this.channelFilter,
    this.recipientUserIdFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminNotificationModel> items;
  final AdminNotificationModel? selected;
  final String? statusFilter;
  final String? channelFilter;
  final int? recipientUserIdFilter;
  final String? errorMessage;

  factory AdminNotificationState.initial() {
    return const AdminNotificationState(isLoading: true);
  }

  AdminNotificationState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminNotificationModel>? items,
    AdminNotificationModel? selected,
    String? statusFilter,
    String? channelFilter,
    int? recipientUserIdFilter,
    String? errorMessage,
    bool clearSelected = false,
    bool clearError = false,
  }) {
    return AdminNotificationState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      selected: clearSelected ? null : selected ?? this.selected,
      statusFilter: statusFilter ?? this.statusFilter,
      channelFilter: channelFilter ?? this.channelFilter,
      recipientUserIdFilter:
          recipientUserIdFilter ?? this.recipientUserIdFilter,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
