import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_product_api.dart';
import 'admin_product_models.dart';

final adminProductRepositoryProvider = Provider<AdminProductRepository>((ref) {
  return AdminProductRepository(api: AdminProductApi());
});

class AdminProductRepository {
  AdminProductRepository({required AdminProductApi api}) : _api = api;

  final AdminProductApi _api;

  Future<List<AdminProduct>> listProducts({
    int page = 1,
    int pageSize = 20,
    String? status,
    int? storeId,
    int? categoryId,
    String? q,
  }) {
    return _api.listProducts(
      page: page,
      pageSize: pageSize,
      status: status,
      storeId: storeId,
      categoryId: categoryId,
      q: q,
    );
  }

  Future<AdminProduct> getProductDetail(int productId) {
    return _api.getProductDetail(productId);
  }

  Future<AdminProduct> updateStatus({
    required int productId,
    required String status,
    String? note,
  }) {
    return _api.updateStatus(productId: productId, status: status, note: note);
  }

  Future<List<AdminProductCategory>> listCategories({String? q}) =>
      _api.listCategories(q: q);

  Future<AdminProductCategory> saveCategory({
    int? id,
    required Map<String, dynamic> data,
  }) => _api.saveCategory(id: id, data: data);
}
