class AdminVerificationDocument {
  const AdminVerificationDocument({
    required this.id,
    required this.documentId,
    required this.documentType,
    required this.fileName,
    required this.status,
  });

  final int id;
  final int documentId;
  final String documentType;
  final String fileName;
  final String status;

  factory AdminVerificationDocument.fromJson(Map<String, dynamic> json) {
    return AdminVerificationDocument(
      id: (json['id'] as num).toInt(),
      documentId: (json['document_id'] as num).toInt(),
      documentType: json['document_type']?.toString() ?? '',
      fileName: json['file_name']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
    );
  }
}

class AdminVerificationReview {
  const AdminVerificationReview({
    required this.id,
    required this.action,
    required this.createdAt,
    this.reviewerId,
    this.note,
  });

  final int id;
  final int? reviewerId;
  final String action;
  final String? note;
  final String createdAt;

  factory AdminVerificationReview.fromJson(Map<String, dynamic> json) {
    return AdminVerificationReview(
      id: (json['id'] as num).toInt(),
      reviewerId:
          json['reviewer_id'] == null
              ? null
              : (json['reviewer_id'] as num).toInt(),
      action: json['action']?.toString() ?? '',
      note: json['note']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminVerificationRequest {
  const AdminVerificationRequest({
    required this.id,
    required this.userId,
    required this.targetRole,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.userEmail,
    this.userPhone,
    this.requestNote,
    this.adminNote,
    this.submittedAt,
    this.reviewedAt,
    this.reviewedBy,
    this.documents = const [],
    this.reviews = const [],
  });

  final int id;
  final int userId;
  final String? userEmail;
  final String? userPhone;
  final String targetRole;
  final String status;
  final String? requestNote;
  final String? adminNote;
  final String? submittedAt;
  final String? reviewedAt;
  final int? reviewedBy;
  final String createdAt;
  final String updatedAt;
  final List<AdminVerificationDocument> documents;
  final List<AdminVerificationReview> reviews;

  factory AdminVerificationRequest.fromJson(Map<String, dynamic> json) {
    final documents = json['documents'] as List? ?? [];
    final reviews = json['reviews'] as List? ?? [];

    return AdminVerificationRequest(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      userEmail: json['user_email']?.toString(),
      userPhone: json['user_phone']?.toString(),
      targetRole: json['target_role']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      requestNote: json['request_note']?.toString(),
      adminNote: json['admin_note']?.toString(),
      submittedAt: json['submitted_at']?.toString(),
      reviewedAt: json['reviewed_at']?.toString(),
      reviewedBy:
          json['reviewed_by'] == null
              ? null
              : (json['reviewed_by'] as num).toInt(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      documents:
          documents
              .map(
                (item) =>
                    AdminVerificationDocument.fromJson((item as Map).cast()),
              )
              .toList(),
      reviews:
          reviews
              .map(
                (item) =>
                    AdminVerificationReview.fromJson((item as Map).cast()),
              )
              .toList(),
    );
  }
}
