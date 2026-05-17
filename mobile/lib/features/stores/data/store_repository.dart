import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'store_api.dart';
import 'store_models.dart';

final storeRepositoryProvider = Provider<StoreRepository>((ref) {
  return StoreRepository(api: StoreApi());
});

class StoreRepository {
  StoreRepository({required StoreApi api}) : _api = api;

  final StoreApi _api;

  Future<List<Store>> listPublicStores({
    String? q,
    int? provinceId,
    int? countyId,
    int? cityId,
    String? storeType,
  }) {
    return _api.listPublicStores(
      q: q,
      provinceId: provinceId,
      countyId: countyId,
      cityId: cityId,
      storeType: storeType,
    );
  }

  Future<Store> getPublicStoreBySlug(String slug) {
    return _api.getPublicStoreBySlug(slug);
  }

  Future<Store?> getMyStore() {
    return _api.getMyStore();
  }

  Future<Store> createStore(StoreCreateInput input) {
    return _api.createStore(input);
  }

  Future<Store> updateStore({
    required int storeId,
    required StoreUpdateInput input,
  }) {
    return _api.updateStore(storeId: storeId, input: input);
  }

  Future<Store> submitStore(int storeId) {
    return _api.submitStore(storeId);
  }
}
