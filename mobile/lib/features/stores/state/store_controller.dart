import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/store_api.dart';
import '../data/store_models.dart';
import '../data/store_repository.dart';
import 'store_state.dart';

final storeControllerProvider =
    StateNotifierProvider<StoreController, StoreState>((ref) {
      return StoreController(repository: ref.watch(storeRepositoryProvider));
    });

class StoreController extends StateNotifier<StoreState> {
  StoreController({required StoreRepository repository})
    : _repository = repository,
      super(StoreState.initial());

  final StoreRepository _repository;

  Future<void> loadPublicStores({
    String? q,
    int? provinceId,
    int? countyId,
    int? cityId,
    String? storeType,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final stores = await _repository.listPublicStores(
        q: q,
        provinceId: provinceId,
        countyId: countyId,
        cityId: cityId,
        storeType: storeType,
      );
      state = state.copyWith(isLoading: false, publicStores: stores);
    } on StoreApiException catch (error) {
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

  Future<void> loadPublicStoreDetail(String slug) async {
    state = state.copyWith(
      isLoading: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final store = await _repository.getPublicStoreBySlug(slug);
      state = state.copyWith(isLoading: false, selectedPublicStore: store);
    } on StoreApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت جزئیات فروشگاه',
      );
    }
  }

  Future<void> loadMyStore() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final store = await _repository.getMyStore();
      state = state.copyWith(
        isLoading: false,
        myStore: store,
        clearMyStore: store == null,
      );
    } on StoreApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت فروشگاه من',
      );
    }
  }

  Future<bool> createStore(StoreCreateInput input) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final store = await _repository.createStore(input);
      state = state.copyWith(isSaving: false, myStore: store);
      return true;
    } on StoreApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ساخت فروشگاه',
      );
      return false;
    }
  }

  Future<bool> updateStore({
    required int storeId,
    required StoreUpdateInput input,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final store = await _repository.updateStore(
        storeId: storeId,
        input: input,
      );
      state = state.copyWith(isSaving: false, myStore: store);
      return true;
    } on StoreApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ویرایش فروشگاه',
      );
      return false;
    }
  }

  Future<bool> submitMyStore() async {
    final store = state.myStore;
    if (store == null) return false;

    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final submitted = await _repository.submitStore(store.id);
      state = state.copyWith(isSaving: false, myStore: submitted);
      return true;
    } on StoreApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ارسال فروشگاه برای بررسی',
      );
      return false;
    }
  }
}
