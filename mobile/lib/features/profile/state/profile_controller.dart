import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../geo/data/geo_repository.dart';
import '../data/profile_api.dart';
import '../data/profile_models.dart';
import '../data/profile_repository.dart';
import 'profile_state.dart';

final profileControllerProvider =
    StateNotifierProvider<ProfileController, ProfileState>((ref) {
      return ProfileController(
        profileRepository: ref.watch(profileRepositoryProvider),
        geoRepository: ref.watch(geoRepositoryProvider),
      );
    });

class ProfileController extends StateNotifier<ProfileState> {
  ProfileController({
    required ProfileRepository profileRepository,
    required GeoRepository geoRepository,
  }) : _profileRepository = profileRepository,
       _geoRepository = geoRepository,
       super(ProfileState.initial());

  final ProfileRepository _profileRepository;
  final GeoRepository _geoRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final profileFuture = _profileRepository.getMe();
      final provincesFuture = _geoRepository.getProvinces();

      final profile = await profileFuture;
      final provinces = await provincesFuture;

      state = state.copyWith(
        isLoading: false,
        profile: profile,
        provinces: provinces,
      );

      if (profile.provinceId != null) {
        await loadCounties(profile.provinceId!);
      }

      if (profile.countyId != null) {
        await loadCities(
          provinceId: profile.provinceId,
          countyId: profile.countyId,
        );
      }
    } on ProfileApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اطلاعات پروفایل',
      );
    }
  }

  Future<void> loadCounties(int provinceId) async {
    try {
      final counties = await _geoRepository.getCounties(provinceId: provinceId);

      state = state.copyWith(
        counties: counties,
        cities: const [],
        clearError: true,
      );
    } catch (_) {
      state = state.copyWith(errorMessage: 'خطا در دریافت شهرستان‌ها');
    }
  }

  Future<void> loadCities({int? provinceId, int? countyId, String? q}) async {
    try {
      final cities = await _geoRepository.getCities(
        provinceId: provinceId,
        countyId: countyId,
        q: q,
      );

      state = state.copyWith(cities: cities, clearError: true);
    } catch (_) {
      state = state.copyWith(errorMessage: 'خطا در دریافت شهرها');
    }
  }

  Future<bool> update(ProfileUpdateInput input) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final profile = await _profileRepository.updateMe(input);

      state = state.copyWith(isSaving: false, profile: profile);

      return true;
    } on ProfileApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ذخیره پروفایل',
      );
      return false;
    }
  }
}
