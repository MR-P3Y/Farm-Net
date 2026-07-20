import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'product_api.dart';
import 'product_models.dart';

final productRepositoryProvider = Provider<ProductRepository>((ref) {
  return ProductRepository(api: ProductApi());
});

class ProductRepository {
  ProductRepository({required ProductApi api}) : _api = api;

  final ProductApi _api;

  Future<List<Product>> listPublicProducts({
    String? q,
    int? storeId,
    int? categoryId,
    int? provinceId,
    int? countyId,
    int? cityId,
    String? storeType,
    num? minPrice,
    num? maxPrice,
    String? sort,
  }) {
    return _api.listPublicProducts(
      q: q,
      storeId: storeId,
      categoryId: categoryId,
      provinceId: provinceId,
      countyId: countyId,
      cityId: cityId,
      storeType: storeType,
      minPrice: minPrice,
      maxPrice: maxPrice,
      sort: sort,
    );
  }

  Future<Product> getPublicProductById(int productId) {
    return _api.getPublicProductById(productId);
  }

  Future<List<Product>> listPublicStoreProducts({
    required String storeSlug,
    String? q,
    int? categoryId,
  }) {
    return _api.listPublicStoreProducts(
      storeSlug: storeSlug,
      q: q,
      categoryId: categoryId,
    );
  }

  Future<Product> getPublicStoreProductBySlug({
    required String storeSlug,
    required String productSlug,
  }) {
    return _api.getPublicStoreProductBySlug(
      storeSlug: storeSlug,
      productSlug: productSlug,
    );
  }

  Future<List<Product>> listMyProducts({
    required int storeId,
    String? status,
    int? categoryId,
    String? q,
  }) {
    return _api.listMyProducts(
      storeId: storeId,
      status: status,
      categoryId: categoryId,
      q: q,
    );
  }

  Future<Product> getMyProduct({required int storeId, required int productId}) {
    return _api.getMyProduct(storeId: storeId, productId: productId);
  }

  Future<Product> createProduct({
    required int storeId,
    required ProductCreateInput input,
  }) {
    return _api.createProduct(storeId: storeId, input: input);
  }

  Future<Product> updateProduct({
    required int storeId,
    required int productId,
    required ProductUpdateInput input,
  }) {
    return _api.updateProduct(
      storeId: storeId,
      productId: productId,
      input: input,
    );
  }

  Future<Product> publishProduct({
    required int storeId,
    required int productId,
  }) {
    return _api.publishProduct(storeId: storeId, productId: productId);
  }

  Future<Product> unpublishProduct({
    required int storeId,
    required int productId,
  }) {
    return _api.unpublishProduct(storeId: storeId, productId: productId);
  }

  Future<Product> archiveProduct({
    required int storeId,
    required int productId,
  }) {
    return _api.archiveProduct(storeId: storeId, productId: productId);
  }

  Future<ProductImage> createProductImage({
    required int storeId,
    required int productId,
    required ProductImageCreateInput input,
  }) {
    return _api.createProductImage(
      storeId: storeId,
      productId: productId,
      input: input,
    );
  }
}
