import 'package:farm_net_admin/features/farms/data/admin_farm_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('farm detail parses only the restricted support contract', () {
    final detail = AdminFarmDetail.fromJson({
      'id': 3,
      'owner_user_id': 8,
      'name': 'مزرعه نمونه',
      'status': 'active',
      'declared_area_sqm': 1200,
      'plots_count': 1,
      'cycles_count': 1,
      'created_at': '2026-07-25T10:00:00Z',
      'updated_at': '2026-07-25T11:00:00Z',
      'plots': [
        {
          'id': 4,
          'name': 'قطعه شمالی',
          'area_sqm': 900,
          'status': 'active',
          'province_id': 1,
          'city_id': 2,
          'cycles_count': 1,
        },
      ],
      'cycles': [
        {
          'id': 5,
          'plot_id': 4,
          'crop_id': 7,
          'variety_id': null,
          'title': 'گندم پاییزه',
          'status': 'planned',
          'planned_start_date': '2026-09-01',
          'planned_end_date': null,
          'actual_start_date': null,
          'actual_end_date': null,
        },
      ],
    });

    expect(detail.summary.ownerUserId, 8);
    expect(detail.plots.single.areaSqm, 900);
    expect(detail.cycles.single.cropId, 7);
  });
}
