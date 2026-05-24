import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_notification_api.dart';
import '../data/admin_notification_repository.dart';
import 'admin_notification_state.dart';

final adminNotificationControllerProvider =
    StateNotifierProvider<AdminNotificationController, AdminNotificationState>((
      ref,
    ) {
      return AdminNotificationController(
        repository: ref.watch(adminNotificationRepositoryProvider),
      );
    });

class AdminNotificationController
    extends StateNotifier<AdminNotificationState> {
  AdminNotificationController({required AdminNotificationRepository repository})
    : _repository = repository,
      super(AdminNotificationState.initial());

  final AdminNotificationRepository _repository;

  Future<void> load({
    String? status,
    String? channel,
    int? recipientUserId,
  }) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      channelFilter: channel,
      recipientUserIdFilter: recipientUserId,
      clearError: true,
    );

    try {
      final items = await _repository.listNotifications(
        status: status,
        channel: channel,
        recipientUserId: recipientUserId,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on AdminNotificationApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اعلان‌ها',
      );
    }
  }

  Future<void> loadDetail(int id) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final item = await _repository.getNotification(id);
      state = state.copyWith(isSaving: false, selected: item);
    } on AdminNotificationApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات اعلان',
      );
    }
  }

  Future<bool> createSystemMessage({
    required int recipientUserId,
    required String title,
    required String body,
    String? actionUrl,
    String priority = 'normal',
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.createSystemMessage(
        recipientUserId: recipientUserId,
        title: title,
        body: body,
        actionUrl: actionUrl,
        priority: priority,
      );

      await load(
        status: state.statusFilter,
        channel: state.channelFilter,
        recipientUserId: state.recipientUserIdFilter,
      );

      state = state.copyWith(isSaving: false);
      return true;
    } on AdminNotificationApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ارسال پیام سیستمی',
      );
      return false;
    }
  }
}
