import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/rental_api.dart';
import '../data/rental_models.dart';
import '../data/rental_repository.dart';
import 'rental_discovery_state.dart';

final rentalDiscoveryControllerProvider =
    StateNotifierProvider<RentalDiscoveryController, RentalDiscoveryState>(
      (ref) => RentalDiscoveryController(
        repository: ref.watch(rentalRepositoryProvider),
        geoRepository: ref.watch(geoRepositoryProvider),
      ),
    );

final rentalEquipmentDetailProvider = FutureProvider.family(
  (ref, int id) => ref.watch(rentalRepositoryProvider).detail(id),
);

class RentalDiscoveryController extends StateNotifier<RentalDiscoveryState> {
  RentalDiscoveryController({
    required RentalRepository repository,
    required GeoRepository geoRepository,
  }) : _repository = repository,
       _geoRepository = geoRepository,
       super(const RentalDiscoveryState());
  final RentalRepository _repository;
  final GeoRepository _geoRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final results = await Future.wait([
        _repository.categories(),
        _geoRepository.getProvinces(),
        _repository.equipment(),
      ]);
      state = state.copyWith(
        isLoading: false,
        categories: results[0] as List<RentalCategory>,
        provinces: results[1] as List<GeoProvince>,
        equipment: results[2] as List<RentalEquipment>,
      );
    } on RentalApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت تجهیزات ناموفق بود.',
      );
    }
  }

  Future<void> apply({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? operatorMode,
  }) async {
    state = state.copyWith(
      isFiltering: true,
      query: query ?? state.query,
      categoryId: categoryId,
      provinceId: provinceId,
      cityId: cityId,
      operatorMode: operatorMode,
      clearError: true,
    );
    try {
      final rows = await _repository.equipment(
        query: state.query,
        categoryId: state.categoryId,
        provinceId: state.provinceId,
        cityId: state.cityId,
        operatorMode: state.operatorMode,
      );
      state = state.copyWith(isFiltering: false, equipment: rows);
    } on RentalApiException catch (error) {
      state = state.copyWith(
        isFiltering: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isFiltering: false,
        errorMessage: 'فیلتر تجهیزات ناموفق بود.',
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
      operatorMode: null,
      cities: const [],
    );
    await apply(
      query: '',
      categoryId: null,
      provinceId: null,
      cityId: null,
      operatorMode: null,
    );
  }
}
