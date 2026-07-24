class RatingSummary {
  const RatingSummary({
    required this.subjectType,
    required this.subjectId,
    required this.ratingAverage,
    required this.reviewsCount,
  });
  final String subjectType;
  final int subjectId;
  final double ratingAverage;
  final int reviewsCount;

  factory RatingSummary.fromJson(Map<String, dynamic> json) => RatingSummary(
    subjectType: json['subject_type']?.toString() ?? '',
    subjectId: (json['subject_id'] as num?)?.toInt() ?? 0,
    ratingAverage:
        double.tryParse(json['rating_average']?.toString() ?? '') ?? 0,
    reviewsCount: (json['reviews_count'] as num?)?.toInt() ?? 0,
  );
}

class PublicReview {
  const PublicReview({
    required this.id,
    required this.score,
    required this.authorName,
    required this.createdAt,
    this.body,
  });
  final int id;
  final int score;
  final String? body;
  final String authorName;
  final DateTime createdAt;

  factory PublicReview.fromJson(Map<String, dynamic> json) => PublicReview(
    id: (json['id'] as num?)?.toInt() ?? 0,
    score: (json['score'] as num?)?.toInt() ?? 0,
    body: json['body']?.toString(),
    authorName:
        ((json['author'] as Map?)?['display_name'])?.toString() ??
        'کاربر فارم‌نت',
    createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ??
        DateTime.fromMillisecondsSinceEpoch(0),
  );
}

class PublicReviewPage {
  const PublicReviewPage({required this.items, required this.rating});
  final List<PublicReview> items;
  final RatingSummary rating;
}

class MyReview {
  const MyReview({
    required this.id,
    required this.sourceType,
    required this.sourceId,
    required this.subjectType,
    required this.subjectId,
    required this.score,
    required this.status,
    required this.canEdit,
    required this.canDelete,
    required this.createdAt,
    this.body,
  });
  final int id;
  final String sourceType;
  final int sourceId;
  final String subjectType;
  final int subjectId;
  final int score;
  final String? body;
  final String status;
  final bool canEdit;
  final bool canDelete;
  final DateTime createdAt;

  factory MyReview.fromJson(Map<String, dynamic> json) => MyReview(
    id: (json['id'] as num?)?.toInt() ?? 0,
    sourceType: json['source_type']?.toString() ?? '',
    sourceId: (json['source_id'] as num?)?.toInt() ?? 0,
    subjectType: json['subject_type']?.toString() ?? '',
    subjectId: (json['subject_id'] as num?)?.toInt() ?? 0,
    score: (json['score'] as num?)?.toInt() ?? 0,
    body: json['body']?.toString(),
    status: json['status']?.toString() ?? '',
    canEdit: json['can_edit'] == true,
    canDelete: json['can_delete'] == true,
    createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ??
        DateTime.fromMillisecondsSinceEpoch(0),
  );
}

class ReviewCreateTarget {
  const ReviewCreateTarget({
    required this.sourceType,
    required this.sourceId,
    required this.subjectType,
    required this.subjectId,
    required this.title,
  });
  final String sourceType;
  final int sourceId;
  final String subjectType;
  final int subjectId;
  final String title;
}

String reviewSubjectLabel(String value) => const {
  'product': 'محصول',
  'store': 'فروشگاه',
  'service_offer': 'خدمت',
  'service_provider': 'خدمات‌دهنده',
  'rental_equipment': 'تجهیز',
  'rental_lessor': 'موجر',
  'consultant': 'مشاور',
}[value] ?? value;
