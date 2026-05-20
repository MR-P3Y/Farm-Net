import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_product_api.dart';
import '../data/admin_product_repository.dart';
import 'admin_product_state.dart';

final adminProductControllerProvider =
    StateNotifierProvider<AdminProductController, AdminProductState>((ref) {
      return AdminProductController(
        repository: ref.watch(adminProductRepositoryProvider),
      );
    });

class AdminProductController extends StateNotifier<AdminProductState> {
  AdminProductController({required AdminProductRepository repository})
    : _repository = repository,
      super(AdminProductState.initial());

  final AdminProductRepository _repository;

  Future<void> load({String? status, String? q}) async {
    final normalizedSearch = q == null || q.trim().isEmpty ? null : q.trim();

    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      search: normalizedSearch,
      clearStatusFilter: status == null,
      clearSearch: normalizedSearch == null,
      clearError: true,
    );

    try {
      final items = await _repository.listProducts(
        status: status,
        q: normalizedSearch,
      );
      state = state.copyWith(isLoading: false, items: items);
    } on AdminProductApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت محصولات',
      );
    }
  }

  Future<void> loadDetail(int productId) async {
    state = state.copyWith(
      isSaving: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final selected = await _repository.getProductDetail(productId);
      state = state.copyWith(isSaving: false, selected: selected);
    } on AdminProductApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات محصول',
      );
    }
  }

  Future<bool> updateStatus({
    required int productId,
    required String status,
    String? note,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateStatus(
        productId: productId,
        status: status,
        note: note,
      );

      final items =
          state.items
              .map((item) => item.id == updated.id ? updated : item)
              .toList();

      state = state.copyWith(isSaving: false, selected: updated, items: items);
      return true;
    } on AdminProductApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت محصول',
      );
      return false;
    }
  }
}
