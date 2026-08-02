import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_repository.dart';
import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import 'consultant_list_state.dart';

final consultantListControllerProvider =
    StateNotifierProvider<ConsultantListController, ConsultantListState>((ref) {
      return ConsultantListController(
        repository: ref.watch(consultantRepositoryProvider),
        geoRepository: ref.watch(geoRepositoryProvider),
      );
    });

class ConsultantListController extends StateNotifier<ConsultantListState> {
  ConsultantListController({
    required ConsultantRepository repository,
    required GeoRepository geoRepository,
  }) : _repository = repository,
       _geoRepository = geoRepository,
       super(ConsultantListState.initial());

  final ConsultantRepository _repository;
  final GeoRepository _geoRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final specialties = await _repository.specialties();
      final provinces = await _geoRepository.getProvinces();
      final consultants = await _repository.list(
        specialtyId: state.selectedSpecialtyId,
        query: state.query,
        sort: state.sort,
        provinceId: state.provinceId,
        cityId: state.cityId,
      );

      state = state.copyWith(
        isLoading: false,
        specialties: specialties,
        provinces: provinces,
        consultants: consultants,
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت فهرست مشاوران ناموفق بود.',
      );
    }
  }

  Future<void> refresh() async {
    await _fetchConsultants(
      specialtyId: state.selectedSpecialtyId,
      query: state.query,
      sort: state.sort,
      provinceId: state.provinceId,
      cityId: state.cityId,
    );
  }

  Future<void> filterBySpecialty(int? specialtyId) async {
    await _fetchConsultants(
      specialtyId: specialtyId,
      query: state.query,
      sort: state.sort,
      provinceId: state.provinceId,
      cityId: state.cityId,
    );
  }

  Future<void> search(String query) async {
    await _fetchConsultants(
      specialtyId: state.selectedSpecialtyId,
      query: query.trim(),
      sort: state.sort,
      provinceId: state.provinceId,
      cityId: state.cityId,
    );
  }

  Future<void> clearFilters() async {
    await _fetchConsultants(
      specialtyId: null,
      query: '',
      sort: state.sort,
      provinceId: null,
      cityId: null,
    );
  }

  Future<void> sortBy(String sort) async {
    await _fetchConsultants(
      specialtyId: state.selectedSpecialtyId,
      query: state.query,
      sort: sort,
      provinceId: state.provinceId,
      cityId: state.cityId,
    );
  }

  Future<List<GeoCity>> loadCities(int? provinceId) async {
    final cities =
        provinceId == null
            ? const <GeoCity>[]
            : await _geoRepository.getCities(provinceId: provinceId);
    state = state.copyWith(cities: cities);
    return cities;
  }

  Future<void> applyFilters({
    required int? specialtyId,
    required int? provinceId,
    required int? cityId,
    required String sort,
  }) => _fetchConsultants(
    specialtyId: specialtyId,
    query: state.query,
    sort: sort,
    provinceId: provinceId,
    cityId: cityId,
  );

  Future<void> clearDiscoveryFilters() async {
    state = state.copyWith(cities: const []);
    await _fetchConsultants(
      specialtyId: null,
      query: state.query,
      sort: 'rating',
      provinceId: null,
      cityId: null,
    );
  }

  Future<void> _fetchConsultants({
    required int? specialtyId,
    required String query,
    required String sort,
    required int? provinceId,
    required int? cityId,
  }) async {
    state = state.copyWith(
      isSaving: true,
      selectedSpecialtyId: specialtyId,
      query: query,
      sort: sort,
      provinceId: provinceId,
      cityId: cityId,
      clearError: true,
    );

    try {
      final consultants = await _repository.list(
        specialtyId: specialtyId,
        query: query,
        sort: sort,
        provinceId: provinceId,
        cityId: cityId,
      );

      state = state.copyWith(isSaving: false, consultants: consultants);
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'جست‌وجوی مشاوران ناموفق بود.',
      );
    }
  }
}
