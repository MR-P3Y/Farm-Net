import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/notification_api.dart';
import '../data/notification_repository.dart';
import 'notification_state.dart';

final notificationControllerProvider =
    StateNotifierProvider<NotificationController, NotificationState>((ref) {
      return NotificationController(
        repository: ref.watch(notificationRepositoryProvider),
      );
    });

class NotificationController extends StateNotifier<NotificationState> {
  NotificationController({required NotificationRepository repository})
    : _repository = repository,
      super(NotificationState.initial());

  final NotificationRepository _repository;

  Future<void> load({String? status}) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      clearStatusFilter: status == null,
      clearError: true,
    );

    try {
      final items = await _repository.listMyNotifications(status: status);
      final unread = await _repository.unreadCount();

      state = state.copyWith(
        isLoading: false,
        items: items,
        unreadCount: unread,
      );
    } on NotificationApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اعلان‌ها',
      );
    }
  }

  Future<void> refresh() {
    return load(status: state.statusFilter);
  }

  Future<bool> markRead(int id) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.markRead(id);
      final items =
          state.items
              .map((item) => item.id == updated.id ? updated : item)
              .toList();
      final unread = await _repository.unreadCount();

      state = state.copyWith(
        isSaving: false,
        items: items,
        unreadCount: unread,
      );

      return true;
    } on NotificationApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در خواندن اعلان',
      );
      return false;
    }
  }

  Future<bool> markAllRead() async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.markAllRead();
      await refresh();

      state = state.copyWith(isSaving: false);
      return true;
    } on NotificationApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در خواندن همه اعلان‌ها',
      );
      return false;
    }
  }

  Future<bool> deleteNotification(int id) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.deleteNotification(id);

      final items = state.items.where((item) => item.id != id).toList();
      final unread = await _repository.unreadCount();

      state = state.copyWith(
        isSaving: false,
        items: items,
        unreadCount: unread,
      );

      return true;
    } on NotificationApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در حذف اعلان');
      return false;
    }
  }
}
