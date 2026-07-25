import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'social_models.dart';

class SocialApiException implements Exception {
  const SocialApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class SocialApi {
  SocialApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<List<SocialPostModel>> posts({
    int? categoryId,
    String? postType,
    String? query,
    int? provinceId,
    int? cityId,
    String? sort,
  }) async {
    final params = <String, dynamic>{};
    if (categoryId != null) params['category_id'] = categoryId;
    if (postType != null) params['post_type'] = postType;
    if (query != null && query.isNotEmpty) params['q'] = query;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (sort != null) params['sort'] = sort;

    try {
      final response = await _client.get('social/posts', queryParameters: params);
      final rows = response.data?['data'] as List? ?? [];
      return rows.map((item) => SocialPostModel.fromJson(item as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<SocialPostModel> postDetail(int id) async {
    try {
      final response = await _client.get('social/posts/$id');
      return SocialPostModel.fromJson(response.data?['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<List<SocialCategoryModel>> categories() async {
    try {
      final response = await _client.get('social/categories');
      final rows = response.data?['data'] as List? ?? [];
      return rows.map((item) => SocialCategoryModel.fromJson(item as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<SocialPostModel> createPost({
    required int? categoryId,
    required String title,
    required String body,
    required String postType,
    int? mediaFileId,
  }) async {
    await _auth();
    try {
      final response = await _client.post('social/posts', data: {
        'category_id': categoryId,
        'title': title,
        'body': body,
        'post_type': postType,
        'media_file_id': mediaFileId,
      });
      return SocialPostModel.fromJson(response.data?['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<List<SocialCommentModel>> comments(int postId) async {
    try {
      final response = await _client.get('social/posts/$postId/comments');
      final rows = response.data?['data'] as List? ?? [];
      return rows.map((item) => SocialCommentModel.fromJson(item as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<SocialCommentModel> createComment({
    required int postId,
    required String body,
    int? parentCommentId,
  }) async {
    await _auth();
    try {
      final response = await _client.post('social/posts/$postId/comments', data: {
        'body': body,
        'parent_comment_id': parentCommentId,
      });
      return SocialCommentModel.fromJson(response.data?['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<void> reactToPost({required int postId, String reactionType = 'like'}) async {
    await _auth();
    try {
      await _client.post('social/posts/$postId/react', data: {'reaction_type': reactionType});
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<void> bookmarkPost(int postId) async {
    await _auth();
    try {
      await _client.post('social/posts/$postId/bookmark', data: {});
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<void> reportPost({required int postId, required String reason, String? description}) async {
    await _auth();
    try {
      await _client.post('social/posts/$postId/report', data: {
        'reason': reason,
        'description': description,
      });
    } on DioException catch (e) {
      throw SocialApiException(_error(e));
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) return ApiError.fromJson(data);
    return ApiError(code: 'NETWORK_ERROR', message: error.message ?? 'خطا در عملیات شبکه اجتماعی');
  }
}
