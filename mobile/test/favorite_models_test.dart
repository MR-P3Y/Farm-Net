import 'package:farm_net/features/favorites/data/favorite_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('favorite item parses shared cross-domain contract', () {
    final item = FavoriteItem.fromJson({
      'id': 8,
      'subject_type': 'service_offer',
      'subject_id': 14,
      'title': 'خاک‌ورزی دقیق',
      'subtitle': 'گرگان',
      'image_url': '/api/v1/media/public/example.jpg',
      'route': '/services/14',
      'is_available': true,
      'created_at': '2026-08-10T10:30:00Z',
    });

    expect(item.subjectType, FavoriteSubjectType.serviceOffer);
    expect(item.subjectId, 14);
    expect(item.route, '/services/14');
    expect(item.isAvailable, isTrue);
  });
}
