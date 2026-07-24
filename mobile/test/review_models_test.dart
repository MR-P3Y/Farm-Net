import 'package:farm_net/features/reviews/data/review_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('public review and rating parse privacy-safe contract', () {
    final page = PublicReviewPage(
      items: [
        PublicReview.fromJson({
          'id': 7,
          'score': 5,
          'body': 'عالی',
          'author': {'display_name': 'کاربر فارم‌نت'},
          'created_at': '2026-07-24T10:00:00',
          'reviewer_user_id': 99,
        }),
      ],
      rating: RatingSummary.fromJson({
        'subject_type': 'product',
        'subject_id': 3,
        'rating_average': '4.50',
        'reviews_count': 2,
      }),
    );
    expect(page.rating.ratingAverage, 4.5);
    expect(page.rating.reviewsCount, 2);
    expect(page.items.single.authorName, 'کاربر فارم‌نت');
    expect(page.items.single.score, 5);
  });

  test('owner review parses lifecycle capabilities', () {
    final review = MyReview.fromJson({
      'id': 1,
      'source_type': 'service_request',
      'source_id': 2,
      'subject_type': 'service_offer',
      'subject_id': 3,
      'score': 4,
      'body': null,
      'status': 'hidden',
      'can_edit': false,
      'can_delete': true,
      'created_at': '2026-07-24T10:00:00',
    });
    expect(review.canEdit, isFalse);
    expect(review.canDelete, isTrue);
    expect(reviewSubjectLabel(review.subjectType), 'خدمت');
  });

  test('all seven shared subject labels are available', () {
    const subjects = [
      'product',
      'store',
      'service_offer',
      'service_provider',
      'rental_equipment',
      'rental_lessor',
      'consultant',
    ];
    expect(subjects.map(reviewSubjectLabel).toSet().length, 7);
  });
}
