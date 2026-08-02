import '../data/consultant_models.dart';
import '../../geo/data/geo_models.dart';

const Object _unset = Object();

class ConsultantListState {
  const ConsultantListState({
    required this.isLoading,
    this.isSaving = false,
    this.specialties = const [],
    this.consultants = const [],
    this.provinces = const [],
    this.cities = const [],
    this.selectedSpecialtyId,
    this.provinceId,
    this.cityId,
    this.query = '',
    this.sort = 'rating',
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<ConsultantSpecialtyModel> specialties;
  final List<ConsultantProfileModel> consultants;
  final List<GeoProvince> provinces;
  final List<GeoCity> cities;
  final int? selectedSpecialtyId;
  final int? provinceId;
  final int? cityId;
  final String query;
  final String sort;
  final String? errorMessage;

  factory ConsultantListState.initial() {
    return const ConsultantListState(isLoading: true);
  }

  ConsultantListState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<ConsultantSpecialtyModel>? specialties,
    List<ConsultantProfileModel>? consultants,
    List<GeoProvince>? provinces,
    List<GeoCity>? cities,
    Object? selectedSpecialtyId = _unset,
    Object? provinceId = _unset,
    Object? cityId = _unset,
    String? query,
    String? sort,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ConsultantListState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      specialties: specialties ?? this.specialties,
      consultants: consultants ?? this.consultants,
      provinces: provinces ?? this.provinces,
      cities: cities ?? this.cities,
      selectedSpecialtyId:
          identical(selectedSpecialtyId, _unset)
              ? this.selectedSpecialtyId
              : selectedSpecialtyId as int?,
      provinceId:
          identical(provinceId, _unset) ? this.provinceId : provinceId as int?,
      cityId: identical(cityId, _unset) ? this.cityId : cityId as int?,
      query: query ?? this.query,
      sort: sort ?? this.sort,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
