import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../farms/data/farm_models.dart';
import '../data/home_dashboard_models.dart';
import '../data/home_dashboard_repository.dart';
import 'home_dashboard_state.dart';

final homeDashboardControllerProvider =
    StateNotifierProvider<HomeDashboardController, HomeDashboardState>(
      (ref) => HomeDashboardController(
        repository: ref.watch(homeDashboardRepositoryProvider),
      ),
    );

class HomeDashboardController extends StateNotifier<HomeDashboardState> {
  HomeDashboardController({
    HomeDashboardRepository? repository,
    Future<HomeDashboardData> Function()? loader,
  }) : assert(repository != null || loader != null),
       _loader = loader ?? repository!.load,
       super(HomeDashboardState.initial());

  static const _selectedFarmKey = 'home_selected_farm_id';
  final Future<HomeDashboardData> Function() _loader;

  Future<void> load() => _load(refreshing: false);

  Future<void> refresh() => _load(refreshing: true);

  Future<void> _load({required bool refreshing}) async {
    state = state.copyWith(
      isLoading: !refreshing,
      isRefreshing: refreshing,
      clearError: true,
    );
    try {
      final data = await _loader();
      final storedId = (await SharedPreferences.getInstance()).getInt(
        _selectedFarmKey,
      );
      final selected = _selectFarm(data.farms, storedId);
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        data: data,
        selectedFarm: selected,
        clearSelectedFarm: selected == null,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        isRefreshing: false,
        errorMessage: 'HOME_DASHBOARD_LOAD_FAILED',
      );
    }
  }

  Future<void> selectFarm(FarmModel farm) async {
    if (!state.data.farms.any((item) => item.id == farm.id)) return;
    state = state.copyWith(selectedFarm: farm);
    await (await SharedPreferences.getInstance()).setInt(
      _selectedFarmKey,
      farm.id,
    );
  }

  FarmModel? _selectFarm(List<FarmModel> farms, int? storedId) {
    if (farms.isEmpty) return null;
    if (storedId != null) {
      for (final farm in farms) {
        if (farm.id == storedId) return farm;
      }
    }
    return farms.first;
  }
}
