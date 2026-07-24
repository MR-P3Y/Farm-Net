import 'package:farm_net_admin/features/reviews/data/admin_review_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('admin review parses typed moderation contract', () {
    final row = AdminReview.fromJson({
      'id': 1,
      'reviewer_user_id': 2,
      'subject_type': 'product',
      'subject_id': 3,
      'score': 5,
      'body': 'عالی',
      'status': 'active',
      'created_at': '2026-07-24T12:00:00',
    });
    expect(row.subjectType, 'product');
    expect(row.score, 5);
    expect(row.status, 'active');
  });

  test('admin report keeps resolution fields typed', () {
    final row = AdminReviewReport.fromJson({
      'id': 4,
      'review_id': 1,
      'reporter_user_id': 5,
      'reason': 'privacy',
      'description': 'اطلاعات شخصی',
      'status': 'resolved',
      'reviewed_by_user_id': 9,
      'resolution_note': 'تأیید شد',
      'created_at': '2026-07-24T12:00:00',
    });
    expect(row.reviewedByUserId, 9);
    expect(row.resolutionNote, 'تأیید شد');
  });

  test('moderation log parses exact audit fields', () {
    final row = AdminReviewLog.fromJson({
      'id': 7,
      'review_id': 1,
      'actor_user_id': 9,
      'report_id': 4,
      'action': 'hidden',
      'from_status': 'active',
      'to_status': 'hidden',
      'note': 'حریم خصوصی',
      'event_key': 'review:1:hidden:unique',
      'created_at': '2026-07-24T12:00:00',
    });
    expect(row.fromStatus, 'active');
    expect(row.toStatus, 'hidden');
    expect(row.eventKey, isNotEmpty);
  });

  test('pagination meta remains explicit', () {
    const page = AdminReviewPage<AdminReview>(
      items: [],
      page: 2,
      total: 41,
      totalPages: 3,
    );
    expect(page.page, 2);
    expect(page.totalPages, 3);
  });
}
