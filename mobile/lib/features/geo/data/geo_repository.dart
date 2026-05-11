import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'geo_api.dart';
import 'geo_models.dart';

final geoRepositoryProvider = Provider<GeoRepository>((ref) {
  return GeoRepository(api: GeoApi());
});

class GeoRepository {
  GeoRepository({required GeoApi api}) : _api = api;

  final GeoApi _api;

  Future<List<GeoProvince>> getProvinces() {
    return _api.getProvinces();
  }

  Future<List<GeoCounty>> getCounties({required int provinceId}) {
    return _api.getCounties(provinceId: provinceId);
  }

  Future<List<GeoCity>> getCities({int? provinceId, int? countyId, String? q}) {
    return _api.getCities(provinceId: provinceId, countyId: countyId, q: q);
  }
}
