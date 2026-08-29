import '../../geo/data/geo_models.dart';
import '../data/service_models.dart';

const _unset = Object();

class ServiceDiscoveryState {
  const ServiceDiscoveryState({
    this.isLoading = true,
    this.isFiltering = false,
    this.categories = const [],
    this.provinces = const [],
    this.cities = const [],
    this.offers = const [],
    this.query = '',
    this.categoryId,
    this.provinceId,
    this.cityId,
    this.pricingType,
    this.sort = 'relevance',
    this.viewMode = ServiceViewMode.list,
    this.userLatitude,
    this.userLongitude,
    this.isLocating = false,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isFiltering;
  final List<ServiceCategory> categories;
  final List<GeoProvince> provinces;
  final List<GeoCity> cities;
  final List<ServiceOffer> offers;
  final String query;
  final int? categoryId;
  final int? provinceId;
  final int? cityId;
  final String? pricingType;
  final String sort;
  final ServiceViewMode viewMode;
  final double? userLatitude;
  final double? userLongitude;
  final bool isLocating;
  final String? errorMessage;

  bool get hasFilters =>
      query.isNotEmpty ||
      categoryId != null ||
      provinceId != null ||
      cityId != null ||
      pricingType != null ||
      sort != 'relevance';

  ServiceDiscoveryState copyWith({
    bool? isLoading,
    bool? isFiltering,
    List<ServiceCategory>? categories,
    List<GeoProvince>? provinces,
    List<GeoCity>? cities,
    List<ServiceOffer>? offers,
    String? query,
    Object? categoryId = _unset,
    Object? provinceId = _unset,
    Object? cityId = _unset,
    Object? pricingType = _unset,
    String? sort,
    ServiceViewMode? viewMode,
    Object? userLatitude = _unset,
    Object? userLongitude = _unset,
    bool? isLocating,
    String? errorMessage,
    bool clearError = false,
  }) => ServiceDiscoveryState(
    isLoading: isLoading ?? this.isLoading,
    isFiltering: isFiltering ?? this.isFiltering,
    categories: categories ?? this.categories,
    provinces: provinces ?? this.provinces,
    cities: cities ?? this.cities,
    offers: offers ?? this.offers,
    query: query ?? this.query,
    categoryId:
        identical(categoryId, _unset) ? this.categoryId : categoryId as int?,
    provinceId:
        identical(provinceId, _unset) ? this.provinceId : provinceId as int?,
    cityId: identical(cityId, _unset) ? this.cityId : cityId as int?,
    pricingType:
        identical(pricingType, _unset)
            ? this.pricingType
            : pricingType as String?,
    sort: sort ?? this.sort,
    viewMode: viewMode ?? this.viewMode,
    userLatitude:
        identical(userLatitude, _unset)
            ? this.userLatitude
            : userLatitude as double?,
    userLongitude:
        identical(userLongitude, _unset)
            ? this.userLongitude
            : userLongitude as double?,
    isLocating: isLocating ?? this.isLocating,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
  );
}

enum ServiceViewMode { list, map }
