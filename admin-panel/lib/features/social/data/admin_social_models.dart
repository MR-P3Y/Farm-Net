class AdminSocialPost {
  const AdminSocialPost({
    required this.id,
    required this.authorUserId,
    required this.title,
    required this.body,
    required this.postType,
    required this.status,
    required this.visibility,
    required this.viewsCount,
    required this.commentsCount,
    required this.reactionsCount,
    required this.reportsCount,
    required this.createdAt,
    this.categoryId,
    this.mediaFileId,
    this.mediaPublicUrl,
  });

  final int id;
  final int authorUserId;
  final int? categoryId;

  final String title;
  final String body;
  final String postType;
  final String status;
  final String visibility;

  final int? mediaFileId;
  final String? mediaPublicUrl;

  final int viewsCount;
  final int commentsCount;
  final int reactionsCount;
  final int reportsCount;

  final String createdAt;

  factory AdminSocialPost.fromJson(Map<String, dynamic> json) {
    return AdminSocialPost(
      id: (json['id'] as num).toInt(),
      authorUserId: (json['author_user_id'] as num).toInt(),
      categoryId:
          json['category_id'] == null
              ? null
              : (json['category_id'] as num).toInt(),
      title: json['title']?.toString() ?? '',
      body: json['body']?.toString() ?? '',
      postType: json['post_type']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      visibility: json['visibility']?.toString() ?? '',
      mediaFileId:
          json['media_file_id'] == null
              ? null
              : (json['media_file_id'] as num).toInt(),
      mediaPublicUrl: json['media_public_url']?.toString(),
      viewsCount: (json['views_count'] as num?)?.toInt() ?? 0,
      commentsCount: (json['comments_count'] as num?)?.toInt() ?? 0,
      reactionsCount: (json['reactions_count'] as num?)?.toInt() ?? 0,
      reportsCount: (json['reports_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminSocialComment {
  const AdminSocialComment({
    required this.id,
    required this.postId,
    required this.authorUserId,
    required this.body,
    required this.status,
    required this.reactionsCount,
    required this.reportsCount,
    required this.createdAt,
    this.parentCommentId,
  });

  final int id;
  final int postId;
  final int authorUserId;
  final int? parentCommentId;

  final String body;
  final String status;

  final int reactionsCount;
  final int reportsCount;

  final String createdAt;

  factory AdminSocialComment.fromJson(Map<String, dynamic> json) {
    return AdminSocialComment(
      id: (json['id'] as num).toInt(),
      postId: (json['post_id'] as num).toInt(),
      authorUserId: (json['author_user_id'] as num).toInt(),
      parentCommentId:
          json['parent_comment_id'] == null
              ? null
              : (json['parent_comment_id'] as num).toInt(),
      body: json['body']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      reactionsCount: (json['reactions_count'] as num?)?.toInt() ?? 0,
      reportsCount: (json['reports_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminSocialReport {
  const AdminSocialReport({
    required this.id,
    required this.reporterUserId,
    required this.targetType,
    required this.reason,
    required this.status,
    required this.createdAt,
    this.postId,
    this.commentId,
    this.description,
    this.reviewedByUserId,
    this.reviewedAt,
  });

  final int id;
  final int reporterUserId;
  final String targetType;

  final int? postId;
  final int? commentId;

  final String reason;
  final String? description;
  final String status;

  final int? reviewedByUserId;
  final String? reviewedAt;

  final String createdAt;

  factory AdminSocialReport.fromJson(Map<String, dynamic> json) {
    return AdminSocialReport(
      id: (json['id'] as num).toInt(),
      reporterUserId: (json['reporter_user_id'] as num).toInt(),
      targetType: json['target_type']?.toString() ?? '',
      postId: json['post_id'] == null ? null : (json['post_id'] as num).toInt(),
      commentId:
          json['comment_id'] == null
              ? null
              : (json['comment_id'] as num).toInt(),
      reason: json['reason']?.toString() ?? '',
      description: json['description']?.toString(),
      status: json['status']?.toString() ?? '',
      reviewedByUserId:
          json['reviewed_by_user_id'] == null
              ? null
              : (json['reviewed_by_user_id'] as num).toInt(),
      reviewedAt: json['reviewed_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AdminSocialCategory {
  const AdminSocialCategory({
    required this.id,
    required this.code,
    required this.title,
    required this.sortOrder,
    required this.isActive,
    required this.postsCount,
    this.description,
  });
  final int id;
  final String code;
  final String title;
  final String? description;
  final int sortOrder;
  final bool isActive;
  final int postsCount;
  factory AdminSocialCategory.fromJson(Map<String, dynamic> json) =>
      AdminSocialCategory(
        id: (json['id'] as num).toInt(),
        code: json['code']?.toString() ?? '',
        title: json['title']?.toString() ?? '',
        description: json['description']?.toString(),
        sortOrder: (json['sort_order'] as num?)?.toInt() ?? 0,
        isActive: json['is_active'] == true,
        postsCount: (json['posts_count'] as num?)?.toInt() ?? 0,
      );
}
