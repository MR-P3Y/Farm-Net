import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net_admin/features/rentals/data/admin_rental_models.dart';

void main() {
  test('admin rental models parse moderation and timeline contracts', () {
    final equipment = AdminRentalEquipment.fromJson({
      'id': 7,
      'lessor_profile_id': 3,
      'title': 'تراکتور',
      'status': 'pending_review',
      'operator_mode': 'either',
      'media': [
        {'id': 1},
      ],
    });
    final request = AdminRentalRequest.fromJson({
      'id': 9,
      'requester_user_id': 10,
      'lessor_profile_id': 3,
      'equipment_id': 7,
      'equipment_title': 'تراکتور',
      'status': 'accepted',
      'currency': 'TOMAN',
      'total_amount_snapshot': '4500000',
      'admin_note': 'بررسی شد',
      'status_logs': [
        {
          'id': 1,
          'from_status': 'pending',
          'to_status': 'accepted',
          'created_at': '2026-07-20T10:00:00',
        },
      ],
    });
    expect(equipment.mediaCount, 1);
    expect(equipment.status, 'pending_review');
    expect(request.totalAmount, 4500000);
    expect(request.adminNote, 'بررسی شد');
    expect(request.statusLogs.single.toStatus, 'accepted');
  });
  test('admin rental page reads pagination metadata', () {
    final page = AdminRentalPage.fromJson({
      'data': [
        {
          'id': 1,
          'code': 'tractors',
          'title': 'تراکتور',
          'sort_order': 100,
          'is_active': true,
        },
      ],
      'meta': {'page': 2, 'total': 25},
    }, AdminRentalCategory.fromJson);
    expect(page.page, 2);
    expect(page.total, 25);
    expect(page.items.single.code, 'tractors');
  });
}
