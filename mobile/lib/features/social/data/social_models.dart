class SocialCategoryModel {
  const SocialCategoryModel({
    required this.id,
    required this.code,
    required this.title,
    required this.isActive,
    this.description,
  });

  final int id;
  final String code;
  final String title;
  final bool isActive;
  final String? description;

  factory SocialCategoryModel.fromJson(Map<String, dynamic> json) {
    return SocialCategoryModel(
      id: (json['id'] as num).toInt(),
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      description: json['description']?.toString(),
      isActive: json['is_active'] == true,
    );
  }
}

class SocialPostModel {
  const SocialPostModel({
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
    this.provinceName,
    this.cityName,
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

  final String? provinceName;
  final String? cityName;

  final int viewsCount;
  final int commentsCount;
  final int reactionsCount;
  final int reportsCount;

  final String createdAt;

  factory SocialPostModel.fromJson(Map<String, dynamic> json) {
    return SocialPostModel(
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
      provinceName: json['province_name']?.toString(),
      cityName: json['city_name']?.toString(),
      viewsCount: (json['views_count'] as num?)?.toInt() ?? 0,
      commentsCount: (json['comments_count'] as num?)?.toInt() ?? 0,
      reactionsCount: (json['reactions_count'] as num?)?.toInt() ?? 0,
      reportsCount: (json['reports_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class SocialCommentModel {
  const SocialCommentModel({
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

  factory SocialCommentModel.fromJson(Map<String, dynamic> json) {
    return SocialCommentModel(
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
