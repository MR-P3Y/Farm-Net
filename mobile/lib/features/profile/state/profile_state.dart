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
    this.errorCode,
    this.errorDetails = const {},
    this.errorTraceId,
  });

  final bool isLoading;
  final bool isSaving;
  final UserProfile? profile;
  final List<GeoProvince> provinces;
  final List<GeoCounty> counties;
  final List<GeoCity> cities;
  final String? errorMessage;
  final String? errorCode;
  final Map<String, dynamic> errorDetails;
  final String? errorTraceId;

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
    String? errorCode,
    Map<String, dynamic>? errorDetails,
    String? errorTraceId,
    bool clearError = false,
    bool clearProfile = false,
  }) {
    return ProfileState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      profile: clearProfile ? null : profile ?? this.profile,
      provinces: provinces ?? this.provinces,
      counties: counties ?? this.counties,
      cities: cities ?? this.cities,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      errorCode: clearError ? null : errorCode ?? this.errorCode,
      errorDetails: clearError ? const {} : errorDetails ?? this.errorDetails,
      errorTraceId: clearError ? null : errorTraceId ?? this.errorTraceId,
    );
  }
}
