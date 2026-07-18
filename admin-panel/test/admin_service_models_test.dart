import 'package:flutter_test/flutter_test.dart';
import 'package:farm_net_admin/features/services/data/admin_service_models.dart';

void main() {
  test('service category parses domain usage counters', () {
    final category = AdminServiceCategory.fromJson({
      'id': 1,
      'code': 'harvesting',
      'title': 'برداشت',
      'sort_order': 100,
      'is_active': true,
      'children_count': 2,
      'provider_links_count': 3,
      'offers_count': 4,
      'requests_count': 5,
    });
    expect(category.childrenCount, 2);
    expect(category.providerLinksCount, 3);
    expect(category.offersCount, 4);
    expect(category.requestsCount, 5);
  });

  test('request detail parses exact typed status logs', () {
    final request = AdminServiceRequest.fromJson({
      'id': 17,
      'requester_user_id': 2,
      'provider_user_id': 8,
      'status': 'accepted',
      'created_at': '2026-07-16T10:00:00Z',
      'status_logs': [
        {
          'id': 3,
          'request_id': 17,
          'changed_by_user_id': 8,
          'old_status': 'open',
          'new_status': 'accepted',
          'note': 'ok',
          'created_at': '2026-07-16T10:05:00Z',
        },
      ],
    });
    expect(request.providerUserId, 8);
    expect(request.statusLogs.single.oldStatus, 'open');
    expect(request.statusLogs.single.newStatus, 'accepted');
  });

  test('paginated offer response stays typed', () {
    final page = AdminServicePage.fromJson({
      'data': [
        {
          'id': 1,
          'provider_profile_id': 4,
          'title': 'سم‌پاشی',
          'status': 'approved',
          'pricing_type': 'fixed',
        },
      ],
      'meta': {'page': 2, 'page_size': 20, 'total': 22},
    }, AdminServiceOffer.fromJson);
    expect(page.items.single, isA<AdminServiceOffer>());
    expect(page.page, 2);
    expect(page.total, 22);
  });
}
