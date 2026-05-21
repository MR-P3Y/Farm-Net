import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/product_api.dart';
import '../data/product_models.dart';
import '../data/product_repository.dart';
import 'product_state.dart';

final productControllerProvider =
    StateNotifierProvider<ProductController, ProductState>((ref) {
      return ProductController(
        repository: ref.watch(productRepositoryProvider),
      );
    });

class ProductController extends StateNotifier<ProductState> {
  ProductController({required ProductRepository repository})
    : _repository = repository,
      super(ProductState.initial());

  final ProductRepository _repository;

  Future<void> loadPublicProducts({String? q}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final items = await _repository.listPublicProducts(q: q);
      state = state.copyWith(isLoading: false, publicProducts: items);
    } on ProductApiException catch (error) {
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

  Future<void> loadPublicProductById(int productId) async {
    state = state.copyWith(
      isLoading: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final item = await _repository.getPublicProductById(productId);
      state = state.copyWith(isLoading: false, selectedProduct: item);
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت جزئیات محصول',
      );
    }
  }

  Future<void> loadStoreProducts({required String storeSlug, String? q}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final items = await _repository.listPublicStoreProducts(
        storeSlug: storeSlug,
        q: q,
      );
      state = state.copyWith(isLoading: false, storeProducts: items);
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت محصولات فروشگاه',
      );
    }
  }

  Future<void> loadMyProducts({
    required int storeId,
    String? status,
    String? q,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final items = await _repository.listMyProducts(
        storeId: storeId,
        status: status,
        q: q,
      );
      state = state.copyWith(isLoading: false, myProducts: items);
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت محصولات من',
      );
    }
  }

  Future<bool> createProduct({
    required int storeId,
    required ProductCreateInput input,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final product = await _repository.createProduct(
        storeId: storeId,
        input: input,
      );
      state = state.copyWith(
        isSaving: false,
        myProducts: [product, ...state.myProducts],
        selectedProduct: product,
      );
      return true;
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ساخت محصول',
      );
      return false;
    }
  }

  Future<bool> updateProduct({
    required int storeId,
    required int productId,
    required ProductUpdateInput input,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateProduct(
        storeId: storeId,
        productId: productId,
        input: input,
      );
      state = state.copyWith(
        isSaving: false,
        selectedProduct: updated,
        myProducts:
            state.myProducts
                .map((item) => item.id == updated.id ? updated : item)
                .toList(),
      );
      return true;
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ویرایش محصول',
      );
      return false;
    }
  }

  Future<bool> publishProduct({required int storeId, required int productId}) {
    return _changeProductStatus(
      storeId: storeId,
      productId: productId,
      publish: true,
    );
  }

  Future<bool> unpublishProduct({
    required int storeId,
    required int productId,
  }) {
    return _changeProductStatus(
      storeId: storeId,
      productId: productId,
      publish: false,
    );
  }

  Future<bool> createProductImage({
    required int storeId,
    required int productId,
    required ProductImageCreateInput input,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.createProductImage(
        storeId: storeId,
        productId: productId,
        input: input,
      );
      state = state.copyWith(isSaving: false);
      return true;
    } on ProductApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ثبت تصویر محصول',
      );
      return false;
    }
  }

  Future<bool> _changeProductStatus({
    required int storeId,
    required int productId,
    required bool publish,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated =
          publish
              ? await _repository.publishProduct(
                storeId: storeId,
                productId: productId,
              )
              : await _repository.unpublishProduct(
                storeId: storeId,
                productId: productId,
              );

      state = state.copyWith(
        isSaving: false,
        selectedProduct: updated,
        myProducts:
            state.myProducts
                .map((item) => item.id == updated.id ? updated : item)
                .toList(),
      );
      return true;
    } on ProductApiException catch (error) {
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
