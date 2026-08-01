import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/home/data/home_dashboard_models.dart';
import 'package:farm_net/features/home/state/home_dashboard_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  const first = FarmModel(id: 1, name: 'First', status: 'active');
  const second = FarmModel(id: 2, name: 'Second', status: 'active');

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('dashboard selects the first farm when no preference exists', () async {
    final controller = HomeDashboardController(
      loader: () async => const HomeDashboardData(farms: [first, second]),
    );

    await controller.load();

    expect(controller.state.isLoading, isFalse);
    expect(controller.state.selectedFarm?.id, 1);
  });

  test('dashboard restores and persists selected farm', () async {
    SharedPreferences.setMockInitialValues({'home_selected_farm_id': 2});
    final controller = HomeDashboardController(
      loader: () async => const HomeDashboardData(farms: [first, second]),
    );

    await controller.load();
    expect(controller.state.selectedFarm?.id, 2);

    await controller.selectFarm(first);
    expect(controller.state.selectedFarm?.id, 1);
    expect(
      (await SharedPreferences.getInstance()).getInt('home_selected_farm_id'),
      1,
    );
  });

  test(
    'dashboard exposes a stable error state when aggregation fails',
    () async {
      final controller = HomeDashboardController(
        loader: () async => throw Exception('network'),
      );

      await controller.load();

      expect(controller.state.isLoading, isFalse);
      expect(controller.state.errorMessage, 'HOME_DASHBOARD_LOAD_FAILED');
    },
  );
}
