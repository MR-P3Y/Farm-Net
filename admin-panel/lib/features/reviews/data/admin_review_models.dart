class AdminReview {
  const AdminReview({
    required this.id,
    required this.reviewerUserId,
    required this.subjectType,
    required this.subjectId,
    required this.score,
    required this.status,
    required this.createdAt,
    this.body,
  });
  final int id;
  final int reviewerUserId;
  final String subjectType;
  final int subjectId;
  final int score;
  final String? body;
  final String status;
  final String createdAt;

  factory AdminReview.fromJson(Map<String, dynamic> json) => AdminReview(
    id: (json['id'] as num?)?.toInt() ?? 0,
    reviewerUserId: (json['reviewer_user_id'] as num?)?.toInt() ?? 0,
    subjectType: json['subject_type']?.toString() ?? '',
    subjectId: (json['subject_id'] as num?)?.toInt() ?? 0,
    score: (json['score'] as num?)?.toInt() ?? 0,
    body: json['body']?.toString(),
    status: json['status']?.toString() ?? '',
    createdAt: json['created_at']?.toString() ?? '',
  );
}

class AdminReviewReport {
  const AdminReviewReport({
    required this.id,
    required this.reviewId,
    required this.reporterUserId,
    required this.reason,
    required this.status,
    required this.createdAt,
    this.description,
    this.reviewedByUserId,
    this.resolutionNote,
  });
  final int id;
  final int reviewId;
  final int reporterUserId;
  final String reason;
  final String? description;
  final String status;
  final int? reviewedByUserId;
  final String? resolutionNote;
  final String createdAt;

  factory AdminReviewReport.fromJson(Map<String, dynamic> json) =>
      AdminReviewReport(
        id: (json['id'] as num?)?.toInt() ?? 0,
        reviewId: (json['review_id'] as num?)?.toInt() ?? 0,
        reporterUserId: (json['reporter_user_id'] as num?)?.toInt() ?? 0,
        reason: json['reason']?.toString() ?? '',
        description: json['description']?.toString(),
        status: json['status']?.toString() ?? '',
        reviewedByUserId: (json['reviewed_by_user_id'] as num?)?.toInt(),
        resolutionNote: json['resolution_note']?.toString(),
        createdAt: json['created_at']?.toString() ?? '',
      );
}

class AdminReviewLog {
  const AdminReviewLog({
    required this.id,
    required this.reviewId,
    required this.action,
    required this.eventKey,
    required this.createdAt,
    this.actorUserId,
    this.reportId,
    this.fromStatus,
    this.toStatus,
    this.note,
  });
  final int id;
  final int reviewId;
  final int? actorUserId;
  final int? reportId;
  final String action;
  final String? fromStatus;
  final String? toStatus;
  final String? note;
  final String eventKey;
  final String createdAt;

  factory AdminReviewLog.fromJson(Map<String, dynamic> json) => AdminReviewLog(
    id: (json['id'] as num?)?.toInt() ?? 0,
    reviewId: (json['review_id'] as num?)?.toInt() ?? 0,
    actorUserId: (json['actor_user_id'] as num?)?.toInt(),
    reportId: (json['report_id'] as num?)?.toInt(),
    action: json['action']?.toString() ?? '',
    fromStatus: json['from_status']?.toString(),
    toStatus: json['to_status']?.toString(),
    note: json['note']?.toString(),
    eventKey: json['event_key']?.toString() ?? '',
    createdAt: json['created_at']?.toString() ?? '',
  );
}

class AdminReviewPage<T> {
  const AdminReviewPage({
    required this.items,
    required this.page,
    required this.total,
    required this.totalPages,
  });
  final List<T> items;
  final int page;
  final int total;
  final int totalPages;
}
