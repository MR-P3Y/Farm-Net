import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_order_api.dart';
import '../data/admin_order_repository.dart';
import 'admin_order_state.dart';

final adminOrderControllerProvider =
    StateNotifierProvider<AdminOrderController, AdminOrderState>((ref) {
      return AdminOrderController(
        repository: ref.watch(adminOrderRepositoryProvider),
      );
    });

class AdminOrderController extends StateNotifier<AdminOrderState> {
  AdminOrderController({required AdminOrderRepository repository})
    : _repository = repository,
      super(AdminOrderState.initial());

  final AdminOrderRepository _repository;

  Future<void> load({String? status, String? paymentStatus}) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      paymentStatusFilter: paymentStatus,
      clearError: true,
    );

    try {
      final items = await _repository.listOrders(
        status: status,
        paymentStatus: paymentStatus,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on AdminOrderApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت سفارش‌ها',
      );
    }
  }

  Future<void> loadDetail(int orderId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final order = await _repository.getOrder(orderId);
      state = state.copyWith(isSaving: false, selected: order);
    } on AdminOrderApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات سفارش',
      );
    }
  }

  Future<bool> updateStatus({
    required int orderId,
    required String status,
    String? adminNote,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateStatus(
        orderId: orderId,
        status: status,
        adminNote: adminNote,
      );

      final items =
          state.items
              .map((item) => item.id == updated.id ? updated : item)
              .toList();

      state = state.copyWith(isSaving: false, selected: updated, items: items);

      return true;
    } on AdminOrderApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت سفارش',
      );
      return false;
    }
  }
}
