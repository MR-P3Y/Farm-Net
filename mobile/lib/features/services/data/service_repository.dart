import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'service_api.dart';
import 'service_models.dart';

final serviceRepositoryProvider = Provider<ServiceRepository>(
  (ref) => ServiceRepository(api: ServiceApi()),
);

class ServiceRepository {
  ServiceRepository({required ServiceApi api}) : _api = api;
  final ServiceApi _api;

  Future<List<ServiceCategory>> categories() => _api.categories();
  Future<List<ServiceOffer>> offers({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
  }) => _api.offers(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    pricingType: pricingType,
  );
  Future<ServiceOffer> detail(int id) => _api.detail(id);
}
