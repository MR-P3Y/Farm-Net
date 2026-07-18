import 'package:farm_net_admin/features/products/data/admin_product_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('product category parses hierarchy and usage counts', () {
    final category = AdminProductCategory.fromJson({
      'id': 2,
      'parent_id': 1,
      'name': 'بذر گندم',
      'slug': 'wheat-seeds',
      'description': 'انواع بذر گندم',
      'sort_order': 10,
      'is_active': true,
      'children_count': 0,
      'products_count': 7,
    });

    expect(category.parentId, 1);
    expect(category.slug, 'wheat-seeds');
    expect(category.productsCount, 7);
    expect(category.isActive, isTrue);
  });
}
