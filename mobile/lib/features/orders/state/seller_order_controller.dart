import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/order_api.dart';
import '../data/order_models.dart';
import '../data/order_repository.dart';

class SellerOrderState {
  const SellerOrderState({
    this.isLoading = false,
    this.isSaving = false,
    this.items = const [],
    this.page = 1,
    this.total = 0,
    this.totalPages = 0,
    this.statusFilter,
    this.selected,
    this.errorMessage,
    this.isDenied = false,
  });

  final bool isLoading;
  final bool isSaving;
  final List<Order> items;
  final int page;
  final int total;
  final int totalPages;
  final String? statusFilter;
  final Order? selected;
  final String? errorMessage;
  final bool isDenied;

  SellerOrderState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<Order>? items,
    int? page,
    int? total,
    int? totalPages,
    String? statusFilter,
    Order? selected,
    String? errorMessage,
    bool? isDenied,
    bool clearStatus = false,
    bool clearSelected = false,
    bool clearError = false,
  }) => SellerOrderState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    items: items ?? this.items,
    page: page ?? this.page,
    total: total ?? this.total,
    totalPages: totalPages ?? this.totalPages,
    statusFilter: clearStatus ? null : statusFilter ?? this.statusFilter,
    selected: clearSelected ? null : selected ?? this.selected,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    isDenied: isDenied ?? this.isDenied,
  );
}

final sellerOrderControllerProvider =
    StateNotifierProvider<SellerOrderController, SellerOrderState>(
      (ref) =>
          SellerOrderController(repository: ref.watch(orderRepositoryProvider)),
    );

class SellerOrderController extends StateNotifier<SellerOrderState> {
  SellerOrderController({required OrderRepository repository})
    : _repository = repository,
      super(const SellerOrderState());

  final OrderRepository _repository;

  Future<void> loadList({int page = 1, String? status}) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      clearStatus: status == null,
      clearError: true,
      isDenied: false,
    );
    try {
      final result = await _repository.listSellerOrders(
        page: page,
        status: status,
      );
      state = state.copyWith(
        isLoading: false,
        items: result.items,
        page: result.page,
        total: result.total,
        totalPages: result.totalPages,
      );
    } on OrderApiException catch (error) {
      _setError(error, loading: false);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت سفارش‌های فروش ناموفق بود.',
      );
    }
  }

  Future<void> loadDetail(int orderId) async {
    state = state.copyWith(
      isLoading: true,
      clearSelected: true,
      clearError: true,
      isDenied: false,
    );
    try {
      final order = await _repository.getSellerOrder(orderId);
      state = state.copyWith(isLoading: false, selected: order);
    } on OrderApiException catch (error) {
      _setError(error, loading: false);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت جزئیات سفارش فروش ناموفق بود.',
      );
    }
  }

  Future<bool> advance({required int orderId, String? sellerNote}) async {
    final order = state.selected;
    final nextStatus = order?.sellerNextStatus;
    if (order == null || order.id != orderId || nextStatus == null) {
      return false;
    }

    state = state.copyWith(isSaving: true, clearError: true, isDenied: false);
    try {
      final updated = await _repository.updateSellerOrderStatus(
        orderId: orderId,
        status: nextStatus,
        sellerNote: sellerNote,
      );
      state = state.copyWith(isSaving: false, selected: updated);
      await loadList(page: state.page, status: state.statusFilter);
      state = state.copyWith(selected: updated);
      return true;
    } on OrderApiException catch (error) {
      _setError(error, saving: false);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'تغییر وضعیت سفارش فروش ناموفق بود.',
      );
      return false;
    }
  }

  void _setError(OrderApiException error, {bool? loading, bool? saving}) {
    final denied = error.error.code == 'PERMISSION_DENIED';
    state = state.copyWith(
      isLoading: loading,
      isSaving: saving,
      isDenied: denied,
      errorMessage:
          denied
              ? 'برای مدیریت سفارش‌های فروش باید مالک فروشگاه تأییدشده باشید.'
              : error.error.message,
    );
  }
}
