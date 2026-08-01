import '../../farms/data/farm_models.dart';
import '../data/home_dashboard_models.dart';

class HomeDashboardState {
  const HomeDashboardState({
    required this.isLoading,
    this.isRefreshing = false,
    this.data = const HomeDashboardData(),
    this.selectedFarm,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isRefreshing;
  final HomeDashboardData data;
  final FarmModel? selectedFarm;
  final String? errorMessage;

  factory HomeDashboardState.initial() =>
      const HomeDashboardState(isLoading: true);

  HomeDashboardState copyWith({
    bool? isLoading,
    bool? isRefreshing,
    HomeDashboardData? data,
    FarmModel? selectedFarm,
    String? errorMessage,
    bool clearSelectedFarm = false,
    bool clearError = false,
  }) => HomeDashboardState(
    isLoading: isLoading ?? this.isLoading,
    isRefreshing: isRefreshing ?? this.isRefreshing,
    data: data ?? this.data,
    selectedFarm: clearSelectedFarm ? null : selectedFarm ?? this.selectedFarm,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
  );
}
