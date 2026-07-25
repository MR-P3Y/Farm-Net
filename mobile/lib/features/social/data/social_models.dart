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
    this.expertAnswers = const [],
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
  final List<ExpertAnswerModel> expertAnswers;

  factory SocialPostModel.fromJson(Map<String, dynamic> json) {
    final expertAnswerRows = json['expert_answers'] as List? ?? const [];

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
      expertAnswers:
          expertAnswerRows
              .whereType<Map<String, dynamic>>()
              .map(ExpertAnswerModel.fromJson)
              .toList(),
    );
  }
}

class ExpertAnswerModel {
  const ExpertAnswerModel({
    required this.id,
    required this.postId,
    required this.expertUserId,
    required this.body,
    required this.status,
    required this.isAccepted,
    required this.helpfulCount,
    required this.reportsCount,
    required this.createdAt,
    required this.updatedAt,
    this.consultant,
  });

  final int id;
  final int postId;
  final int expertUserId;
  final String body;
  final String status;
  final bool isAccepted;
  final int helpfulCount;
  final int reportsCount;
  final String createdAt;
  final String updatedAt;
  final ExpertAnswerConsultantModel? consultant;

  factory ExpertAnswerModel.fromJson(Map<String, dynamic> json) {
    final consultantJson = json['consultant'];

    return ExpertAnswerModel(
      id:
          (json['answer_id'] as num?)?.toInt() ??
          (json['id'] as num?)?.toInt() ??
          0,
      postId: (json['post_id'] as num?)?.toInt() ?? 0,
      expertUserId:
          (json['expert_user_id'] as num?)?.toInt() ??
          (json['expert_id'] as num?)?.toInt() ??
          0,
      body: json['body']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      isAccepted: json['is_accepted'] == true,
      helpfulCount: (json['helpful_count'] as num?)?.toInt() ?? 0,
      reportsCount: (json['reports_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      consultant:
          consultantJson is Map<String, dynamic>
              ? ExpertAnswerConsultantModel.fromJson(consultantJson)
              : null,
    );
  }
}

class ExpertAnswerConsultantModel {
  const ExpertAnswerConsultantModel({
    required this.consultantId,
    required this.userId,
    required this.status,
    required this.isVerified,
    required this.isFeatured,
    required this.ratingAverage,
    required this.reviewsCount,
    this.displayName,
    this.name,
    this.title,
    this.avatarFileId,
    this.avatarMediaFileId,
    this.avatarUrl,
    this.verificationStatus,
    this.specialties = const [],
  });

  final int consultantId;
  final int userId;
  final String? displayName;
  final String? name;
  final String? title;
  final String? avatarFileId;
  final int? avatarMediaFileId;
  final String? avatarUrl;
  final String status;
  final bool isVerified;
  final String? verificationStatus;
  final bool isFeatured;
  final double ratingAverage;
  final int reviewsCount;
  final List<ExpertAnswerSpecialtyModel> specialties;

  String get resolvedName {
    final primary = displayName?.trim();
    if (primary != null && primary.isNotEmpty) return primary;

    final fallback = name?.trim();
    if (fallback != null && fallback.isNotEmpty) return fallback;

    return 'مشاور';
  }

  factory ExpertAnswerConsultantModel.fromJson(Map<String, dynamic> json) {
    final specialtyRows = json['specialties'] as List? ?? const [];

    return ExpertAnswerConsultantModel(
      consultantId:
          (json['consultant_id'] as num?)?.toInt() ??
          (json['id'] as num?)?.toInt() ??
          0,
      userId: (json['user_id'] as num?)?.toInt() ?? 0,
      displayName: json['display_name']?.toString(),
      name: json['name']?.toString(),
      title: json['title']?.toString(),
      avatarFileId: json['avatar_file_id']?.toString(),
      avatarMediaFileId:
          json['avatar_media_file_id'] == null
              ? null
              : (json['avatar_media_file_id'] as num).toInt(),
      avatarUrl: json['avatar_url']?.toString(),
      status: json['status']?.toString() ?? '',
      isVerified: json['is_verified'] == true,
      verificationStatus: json['verification_status']?.toString(),
      isFeatured: json['is_featured'] == true,
      ratingAverage: (json['rating_average'] as num?)?.toDouble() ?? 0,
      reviewsCount: (json['reviews_count'] as num?)?.toInt() ?? 0,
      specialties:
          specialtyRows
              .whereType<Map<String, dynamic>>()
              .map(ExpertAnswerSpecialtyModel.fromJson)
              .toList(),
    );
  }
}

class ExpertAnswerSpecialtyModel {
  const ExpertAnswerSpecialtyModel({
    required this.id,
    required this.code,
    required this.title,
  });

  final int id;
  final String code;
  final String title;

  factory ExpertAnswerSpecialtyModel.fromJson(Map<String, dynamic> json) {
    return ExpertAnswerSpecialtyModel(
      id: (json['id'] as num?)?.toInt() ?? 0,
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
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

class SocialFeedResponse {
  const SocialFeedResponse({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
  });
  final List<SocialPostModel> items;
  final int total;
  final int page;
  final int pageSize;

  factory SocialFeedResponse.fromJson(Map<String, dynamic> json) => SocialFeedResponse(
    items: (json['items'] as List? ?? []).map((i) => SocialPostModel.fromJson(i as Map<String, dynamic>)).toList(),
    total: (json['total'] as num?)?.toInt() ?? 0,
    page: (json['page'] as num?)?.toInt() ?? 1,
    pageSize: (json['page_size'] as num?)?.toInt() ?? 10,
  );
}

class SocialCreatePostInput {
  const SocialCreatePostInput({
    required this.title,
    required this.body,
    required this.postType,
    this.categoryId,
    this.mediaFileId,
  });
  final String title;
  final String body;
  final String postType;
  final int? categoryId;
  final int? mediaFileId;

  Map<String, dynamic> toJson() => {
    'title': title,
    'body': body,
    'post_type': postType,
    'category_id': categoryId,
    'media_file_id': mediaFileId,
  };
}
