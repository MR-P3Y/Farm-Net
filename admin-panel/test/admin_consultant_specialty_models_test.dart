import 'package:farm_net_admin/features/consultants/data/admin_consultant_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('consultant specialty parses profile and request usage', () {
    final item = AdminConsultSpecialty.fromJson({
      'id': 1,
      'code': 'plant_nutrition',
      'title': 'تغذیه گیاه',
      'sort_order': 100,
      'is_active': true,
      'profiles_count': 7,
      'requests_count': 11,
    });
    expect(item.profilesCount, 7);
    expect(item.requestsCount, 11);
  });
}
