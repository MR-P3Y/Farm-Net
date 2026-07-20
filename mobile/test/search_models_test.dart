import 'package:farm_net/features/search/data/search_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('unified search parses grouped typed results and decimal strings', () {
    final result = UnifiedSearchResult.fromJson({
      'query': 'تراکتور',
      'total': 1,
      'groups': [
        {
          'type': 'rental_equipment',
          'total': 1,
          'page': 1,
          'page_size': 10,
          'items': [
            {
              'type': 'rental_equipment',
              'resource_id': 7,
              'title': 'تراکتور باغی',
              'route': '/rentals/equipment/7',
              'price': '2500000.00',
              'currency': 'TOMAN',
              'rating': '4.5',
            },
          ],
        },
      ],
    });

    expect(result.total, 1);
    expect(result.groups.single.type, 'rental_equipment');
    expect(result.groups.single.items.single.price, 2500000);
    expect(result.groups.single.items.single.route, '/rentals/equipment/7');
  });

  test('unified search safely defaults optional and malformed values', () {
    final item = SearchResultItem.fromJson({'title': 'مطلب'});
    expect(item.resourceId, 0);
    expect(item.route, '');
    expect(item.price, isNull);
  });
}
