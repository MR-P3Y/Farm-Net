import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';

import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/service_api.dart';
import '../data/service_models.dart';
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
        offers: _sortOffers(offers),
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
    String? sort,
  }) async {
    state = state.copyWith(
      isFiltering: true,
      query: query ?? state.query,
      categoryId: categoryId,
      provinceId: provinceId,
      cityId: cityId,
      pricingType: pricingType,
      sort: sort ?? state.sort,
      clearError: true,
    );
    try {
      final offers = await _repository.offers(
        query: state.query,
        categoryId: state.categoryId,
        provinceId: state.provinceId,
        cityId: state.cityId,
        pricingType: state.pricingType,
        sort: state.sort,
        latitude: state.userLatitude,
        longitude: state.userLongitude,
      );
      state = state.copyWith(isFiltering: false, offers: _sortOffers(offers));
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
      sort: 'relevance',
      cities: const [],
    );
    await apply(
      query: '',
      categoryId: null,
      provinceId: null,
      cityId: null,
      pricingType: null,
      sort: 'relevance',
    );
  }

  void setViewMode(ServiceViewMode mode) {
    state = state.copyWith(viewMode: mode);
  }

  Future<void> setSort(String sort) => apply(sort: sort);

  Future<void> useCurrentLocation() async {
    state = state.copyWith(isLocating: true, clearError: true);
    try {
      if (!await Geolocator.isLocationServiceEnabled()) {
        throw const ServiceLocationException('Location services are disabled.');
      }
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw const ServiceLocationException('Location permission was denied.');
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );
      state = state.copyWith(
        userLatitude: position.latitude,
        userLongitude: position.longitude,
        isLocating: false,
        sort: 'distance',
        offers: _sortOffers(
          state.offers,
          latitude: position.latitude,
          longitude: position.longitude,
          sort: 'distance',
        ),
      );
    } on ServiceLocationException catch (error) {
      state = state.copyWith(isLocating: false, errorMessage: error.message);
    } catch (_) {
      state = state.copyWith(
        isLocating: false,
        errorMessage: 'Could not read the current location.',
      );
    }
  }

  List<ServiceOffer> _sortOffers(
    List<ServiceOffer> offers, {
    String? sort,
    double? latitude,
    double? longitude,
  }) {
    final selectedSort = sort ?? state.sort;
    final lat = latitude ?? state.userLatitude;
    final lng = longitude ?? state.userLongitude;
    final result = [...offers];
    if (selectedSort == 'distance' && lat != null && lng != null) {
      result.sort(
        (a, b) => _distance(a, lat, lng).compareTo(_distance(b, lat, lng)),
      );
    }
    return result;
  }

  static double _distance(
    ServiceOffer offer,
    double latitude,
    double longitude,
  ) {
    if (offer.latitude == null || offer.longitude == null) {
      return double.infinity;
    }
    return Geolocator.distanceBetween(
      latitude,
      longitude,
      offer.latitude!,
      offer.longitude!,
    );
  }
}

class ServiceLocationException implements Exception {
  const ServiceLocationException(this.message);
  final String message;
}
