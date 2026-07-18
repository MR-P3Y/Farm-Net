import 'package:farm_net_admin/features/taxonomies/presentation/admin_taxonomies_page.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('taxonomy hub has unique permission-aware domain destinations', () {
    expect(adminTaxonomyDestinations, hasLength(4));
    expect(
      adminTaxonomyDestinations.map((item) => item.permission).toSet(),
      hasLength(4),
    );
    expect(
      adminTaxonomyDestinations.map((item) => item.location).toSet(),
      hasLength(4),
    );
    expect(
      adminTaxonomyDestinations
          .firstWhere((item) => item.permission == 'consult_specialties.read')
          .location,
      '/consultant-specialties',
    );
  });
}
