import 'package:farm_net_admin/features/social/data/admin_social_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('social category parses activation and post count', () {
    final item = AdminSocialCategory.fromJson({
      'id': 1,
      'code': 'general',
      'title': 'عمومی',
      'sort_order': 100,
      'is_active': true,
      'posts_count': 9,
    });
    expect(item.code, 'general');
    expect(item.postsCount, 9);
    expect(item.isActive, isTrue);
  });
}
