import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net/features/rentals/data/rental_models.dart';

void main() {
  test('rental equipment parses public contract and primary media', () {
    final item = RentalEquipment.fromJson({
      'id': 7,
      'lessor_profile_id': 3,
      'category_id': 2,
      'title': 'تراکتور رومانی',
      'operator_mode': 'either',
      'currency': 'TOMAN',
      'security_deposit_amount': '500000',
      'lessor_display_name': 'موجر نمونه',
      'category': {'id': 2, 'code': 'tractors', 'title': 'تراکتور'},
      'media': [
        {
          'id': 1,
          'public_url': '/api/v1/media/public/tractor.jpg',
          'is_primary': true,
        },
      ],
    });
    expect(item.id, 7);
    expect(item.category?.code, 'tractors');
    expect(item.primaryMedia?.publicUrl, contains('tractor.jpg'));
    expect(item.securityDepositAmount, 500000);
    expect(rentalOperatorLabel(item.operatorMode), 'با یا بدون اپراتور');
  });

  test('rental pricing parses decimal strings and unit labels', () {
    final price = RentalPricingRule.fromJson({
      'id': 4,
      'unit': 'hectare',
      'operator_included': true,
      'price_amount': '2500000.00',
      'minimum_units': '2.00',
      'currency': 'TOMAN',
    });
    expect(price.priceAmount, 2500000);
    expect(price.minimumUnits, 2);
    expect(price.operatorIncluded, isTrue);
    expect(rentalUnitLabel(price.unit), 'هکتار');
  });
}
