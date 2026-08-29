import 'package:farm_net/features/geo/data/geo_api.dart';
import 'package:farm_net/features/geo/data/geo_models.dart';
import 'package:farm_net/features/geo/data/geo_repository.dart';
import 'package:farm_net/features/services/data/service_api.dart';
import 'package:farm_net/features/services/data/service_models.dart';
import 'package:farm_net/features/services/data/service_repository.dart';
import 'package:farm_net/features/services/state/service_discovery_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'search preserves active service filters and explicit null clears one',
    () async {
      final controller = ServiceDiscoveryController(
        repository: _ServiceRepository(),
        geoRepository: _GeoRepository(),
      );

      await controller.apply(
        categoryId: 7,
        provinceId: 2,
        cityId: 3,
        pricingType: 'fixed',
        sort: 'newest',
      );
      await controller.apply(query: 'سم‌پاشی');

      expect(controller.state.query, 'سم‌پاشی');
      expect(controller.state.categoryId, 7);
      expect(controller.state.provinceId, 2);
      expect(controller.state.cityId, 3);
      expect(controller.state.pricingType, 'fixed');
      expect(controller.state.sort, 'newest');

      await controller.apply(categoryId: null);
      expect(controller.state.categoryId, isNull);
      expect(controller.state.provinceId, 2);
      expect(controller.state.cityId, 3);
      expect(controller.state.pricingType, 'fixed');
    },
  );
}

class _ServiceRepository extends ServiceRepository {
  _ServiceRepository() : super(api: ServiceApi());

  @override
  Future<List<ServiceOffer>> offers({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
    num? minPrice,
    num? maxPrice,
    String? sort,
    double? latitude,
    double? longitude,
    double? radiusKm,
  }) async => const [];
}

class _GeoRepository extends GeoRepository {
  _GeoRepository() : super(api: GeoApi());

  @override
  Future<List<GeoProvince>> getProvinces() async => const [];

  @override
  Future<List<GeoCity>> getCities({
    int? provinceId,
    int? countyId,
    String? q,
  }) async => const [];
}
