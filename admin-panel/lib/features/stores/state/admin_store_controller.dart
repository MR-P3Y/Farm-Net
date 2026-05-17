import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_store_api.dart';
import '../data/admin_store_repository.dart';
import 'admin_store_state.dart';

final adminStoreControllerProvider =
    StateNotifierProvider<AdminStoreController, AdminStoreState>((ref) {
      return AdminStoreController(
        repository: ref.watch(adminStoreRepositoryProvider),
      );
    });

class AdminStoreController extends StateNotifier<AdminStoreState> {
  AdminStoreController({required AdminStoreRepository repository})
    : _repository = repository,
      super(AdminStoreState.initial());

  final AdminStoreRepository _repository;

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
      final items = await _repository.listStores(
        status: status,
        q: normalizedSearch,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on AdminStoreApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت فروشگاه‌ها',
      );
    }
  }

  Future<void> loadDetail(int storeId) async {
    state = state.copyWith(
      isSaving: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final selected = await _repository.getStoreDetail(storeId);

      state = state.copyWith(isSaving: false, selected: selected);
    } on AdminStoreApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات فروشگاه',
      );
    }
  }

  Future<bool> updateStatus({
    required int storeId,
    required String status,
    String? note,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateStatus(
        storeId: storeId,
        status: status,
        note: note,
      );

      final items =
          state.items
              .map((item) => item.id == updated.id ? updated : item)
              .toList();

      state = state.copyWith(isSaving: false, selected: updated, items: items);

      return true;
    } on AdminStoreApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت فروشگاه',
      );
      return false;
    }
  }
}
