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

  test(
    'rental request input preserves backend operator and range contract',
    () {
      final input =
          RentalRequestInput(
            equipmentId: 7,
            pricingRuleId: 4,
            startsAt: DateTime.utc(2026, 8, 1),
            endsAt: DateTime.utc(2026, 8, 3),
            requestedUnits: 2,
            operatorRequested: true,
            requesterNote: ' نیاز به راننده ',
          ).toJson();
      expect(input['equipment_id'], 7);
      expect(input['pricing_rule_id'], 4);
      expect(input['operator_requested'], isTrue);
      expect(input['requester_note'], 'نیاز به راننده');
    },
  );

  test('rental request parses snapshots timeline and cancel eligibility', () {
    final request = RentalRequest.fromJson({
      'id': 9,
      'equipment_id': 7,
      'pricing_rule_id': 4,
      'equipment_title': 'تراکتور',
      'starts_at': '2026-08-01T00:00:00',
      'ends_at': '2026-08-03T00:00:00',
      'requested_units': '2.00',
      'operator_requested': false,
      'status': 'accepted',
      'currency': 'TOMAN',
      'total_amount_snapshot': '4500000.00',
      'status_logs': [
        {
          'id': 1,
          'from_status': 'pending',
          'to_status': 'accepted',
          'created_at': '2026-07-20T10:00:00',
        },
      ],
    });
    expect(request.canCancel, isTrue);
    expect(request.totalAmount, 4500000);
    expect(request.statusLogs.single.toStatus, 'accepted');
    expect(rentalRequestStatusLabel(request.status), 'پذیرفته‌شده');
  });

  test('lessor profile and owner equipment expose real lifecycle helpers', () {
    final profile = LessorProfile.fromJson({
      'id': 3,
      'status': 'rejected',
      'equipment_count': 2,
      'admin_note': 'اصلاح نشانی',
    });
    final equipment = RentalEquipmentOwner.fromJson({
      'id': 7,
      'lessor_profile_id': 3,
      'title': 'تراکتور',
      'slug': 'tractor',
      'operator_mode': 'without_operator',
      'currency': 'TOMAN',
      'status': 'draft',
      'media': [
        {'id': 11, 'media_file_id': 44, 'is_primary': true},
      ],
    });
    expect(profile.canEdit, isTrue);
    expect(profile.adminNote, 'اصلاح نشانی');
    expect(equipment.canSubmit, isTrue);
    expect(equipment.media.single.mediaFileId, 44);
  });

  test('lessor workbench exposes only backend transition matrix', () {
    RentalRequest request(String status) => RentalRequest.fromJson({
      'id': 9,
      'equipment_id': 7,
      'pricing_rule_id': 4,
      'equipment_title': 'تراکتور',
      'starts_at': '2026-08-01T00:00:00',
      'ends_at': '2026-08-03T00:00:00',
      'requested_units': 2,
      'operator_requested': false,
      'status': status,
      'currency': 'TOMAN',
    });
    expect(request('pending').lessorNextStatuses, ['accepted', 'rejected']);
    expect(request('accepted').lessorNextStatuses, ['in_progress']);
    expect(request('in_progress').lessorNextStatuses, ['completed']);
    expect(request('completed').lessorNextStatuses, isEmpty);
  });
}
