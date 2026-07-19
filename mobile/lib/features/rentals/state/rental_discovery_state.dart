import '../../geo/data/geo_models.dart';
import '../data/rental_models.dart';

const _unset = Object();

class RentalDiscoveryState {
  const RentalDiscoveryState({
    this.isLoading = true,
    this.isFiltering = false,
    this.categories = const [],
    this.provinces = const [],
    this.cities = const [],
    this.equipment = const [],
    this.query = '',
    this.categoryId,
    this.provinceId,
    this.cityId,
    this.operatorMode,
    this.errorMessage,
  });
  final bool isLoading;
  final bool isFiltering;
  final List<RentalCategory> categories;
  final List<GeoProvince> provinces;
  final List<GeoCity> cities;
  final List<RentalEquipment> equipment;
  final String query;
  final int? categoryId;
  final int? provinceId;
  final int? cityId;
  final String? operatorMode;
  final String? errorMessage;

  bool get hasFilters =>
      query.isNotEmpty ||
      categoryId != null ||
      provinceId != null ||
      cityId != null ||
      operatorMode != null;

  RentalDiscoveryState copyWith({
    bool? isLoading,
    bool? isFiltering,
    List<RentalCategory>? categories,
    List<GeoProvince>? provinces,
    List<GeoCity>? cities,
    List<RentalEquipment>? equipment,
    String? query,
    Object? categoryId = _unset,
    Object? provinceId = _unset,
    Object? cityId = _unset,
    Object? operatorMode = _unset,
    String? errorMessage,
    bool clearError = false,
  }) => RentalDiscoveryState(
    isLoading: isLoading ?? this.isLoading,
    isFiltering: isFiltering ?? this.isFiltering,
    categories: categories ?? this.categories,
    provinces: provinces ?? this.provinces,
    cities: cities ?? this.cities,
    equipment: equipment ?? this.equipment,
    query: query ?? this.query,
    categoryId:
        identical(categoryId, _unset) ? this.categoryId : categoryId as int?,
    provinceId:
        identical(provinceId, _unset) ? this.provinceId : provinceId as int?,
    cityId: identical(cityId, _unset) ? this.cityId : cityId as int?,
    operatorMode:
        identical(operatorMode, _unset)
            ? this.operatorMode
            : operatorMode as String?,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
  );
}
