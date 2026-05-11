import '../../geo/data/geo_models.dart';
import '../data/profile_models.dart';

class ProfileState {
  const ProfileState({
    required this.isLoading,
    this.isSaving = false,
    this.profile,
    this.provinces = const [],
    this.counties = const [],
    this.cities = const [],
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final UserProfile? profile;
  final List<GeoProvince> provinces;
  final List<GeoCounty> counties;
  final List<GeoCity> cities;
  final String? errorMessage;

  factory ProfileState.initial() {
    return const ProfileState(isLoading: true);
  }

  ProfileState copyWith({
    bool? isLoading,
    bool? isSaving,
    UserProfile? profile,
    List<GeoProvince>? provinces,
    List<GeoCounty>? counties,
    List<GeoCity>? cities,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ProfileState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      profile: profile ?? this.profile,
      provinces: provinces ?? this.provinces,
      counties: counties ?? this.counties,
      cities: cities ?? this.cities,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
