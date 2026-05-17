import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_store_api.dart';
import 'admin_store_models.dart';

final adminStoreRepositoryProvider = Provider<AdminStoreRepository>((ref) {
  return AdminStoreRepository(api: AdminStoreApi());
});

class AdminStoreRepository {
  AdminStoreRepository({required AdminStoreApi api}) : _api = api;

  final AdminStoreApi _api;

  Future<List<AdminStore>> listStores({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? q,
  }) {
    return _api.listStores(
      page: page,
      pageSize: pageSize,
      status: status,
      q: q,
    );
  }

  Future<AdminStore> getStoreDetail(int storeId) {
    return _api.getStoreDetail(storeId);
  }

  Future<AdminStore> updateStatus({
    required int storeId,
    required String status,
    String? note,
  }) {
    return _api.updateStatus(storeId: storeId, status: status, note: note);
  }
}
