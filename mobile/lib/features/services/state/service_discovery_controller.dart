import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/service_api.dart';
import '../data/service_repository.dart';
import 'service_discovery_state.dart';

final serviceDiscoveryControllerProvider =
    StateNotifierProvider<ServiceDiscoveryController, ServiceDiscoveryState>(
      (ref) => ServiceDiscoveryController(
        repository: ref.watch(serviceRepositoryProvider),
        geoRepository: ref.watch(geoRepositoryProvider),
      ),
    );

final serviceOfferDetailProvider = FutureProvider.family(
  (ref, int id) => ref.watch(serviceRepositoryProvider).detail(id),
);

class ServiceDiscoveryController extends StateNotifier<ServiceDiscoveryState> {
  ServiceDiscoveryController({
    required ServiceRepository repository,
    required GeoRepository geoRepository,
  }) : _repository = repository,
       _geoRepository = geoRepository,
       super(const ServiceDiscoveryState());

  final ServiceRepository _repository;
  final GeoRepository _geoRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final categoriesFuture = _repository.categories();
      final provincesFuture = _geoRepository.getProvinces();
      final offersFuture = _repository.offers();
      final categories = await categoriesFuture;
      final provinces = await provincesFuture;
      final offers = await offersFuture;
      state = state.copyWith(
        isLoading: false,
        categories: categories,
        provinces: provinces,
        offers: offers,
      );
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت خدمات ناموفق بود.',
      );
    }
  }

  Future<void> apply({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
  }) async {
    state = state.copyWith(
      isFiltering: true,
      query: query ?? state.query,
      categoryId: categoryId,
      provinceId: provinceId,
      cityId: cityId,
      pricingType: pricingType,
      clearError: true,
    );
    try {
      final offers = await _repository.offers(
        query: state.query,
        categoryId: state.categoryId,
        provinceId: state.provinceId,
        cityId: state.cityId,
        pricingType: state.pricingType,
      );
      state = state.copyWith(isFiltering: false, offers: offers);
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isFiltering: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isFiltering: false,
        errorMessage: 'فیلتر خدمات ناموفق بود.',
      );
    }
  }

  Future<void> selectProvince(int? provinceId) async {
    final cities =
        provinceId == null
            ? const <GeoCity>[]
            : await _geoRepository.getCities(provinceId: provinceId);
    state = state.copyWith(
      provinceId: provinceId,
      cityId: null,
      cities: cities,
    );
  }

  Future<void> clear() async {
    state = state.copyWith(
      query: '',
      categoryId: null,
      provinceId: null,
      cityId: null,
      pricingType: null,
      cities: const [],
    );
    await apply(
      query: '',
      categoryId: null,
      provinceId: null,
      cityId: null,
      pricingType: null,
    );
  }
}
