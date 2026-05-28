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
  String toString() => '${error.code}: ${error.message}';
}

class SocialApi {
  SocialApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<List<SocialCategoryModel>> categories() async {
    final json = await _get('/social/categories');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => SocialCategoryModel.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<List<SocialPostModel>> posts({
    int? categoryId,
    String? postType,
    String? query,
  }) async {
    final params = <String, String>{'page': '1', 'page_size': '30'};

    if (categoryId != null) params['category_id'] = categoryId.toString();
    if (postType != null && postType.isNotEmpty) {
      params['post_type'] = postType;
    }
    if (query != null && query.trim().isNotEmpty) {
      params['q'] = query.trim();
    }

    final uri = Uri(path: '/social/posts', queryParameters: params);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => SocialPostModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<SocialPostModel> postDetail(int postId) async {
    final json = await _get('/social/posts/$postId');
    return SocialPostModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<SocialPostModel> createPost({
    required int? categoryId,
    required String title,
    required String body,
    required String postType,
    int? mediaFileId,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/social/posts',
      data: {
        'category_id': categoryId,
        'title': title,
        'body': body,
        'post_type': postType,
        'visibility': 'public',
        'media_file_id': mediaFileId,
      },
    );

    return SocialPostModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<SocialCommentModel>> comments(int postId) async {
    final json = await _get(
      '/social/posts/$postId/comments?page=1&page_size=100',
    );
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => SocialCommentModel.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<SocialCommentModel> createComment({
    required int postId,
    required String body,
    int? parentCommentId,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/social/posts/$postId/comments',
      data: {'body': body, 'parent_comment_id': parentCommentId},
    );

    return SocialCommentModel.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<void> reactToPost({
    required int postId,
    String reactionType = 'like',
  }) async {
    await _setStoredToken();

    await _post(
      '/social/posts/$postId/reactions',
      data: {'reaction_type': reactionType},
    );
  }

  Future<void> bookmarkPost(int postId) async {
    await _setStoredToken();
    await _post('/social/posts/$postId/bookmark');
  }

  Future<void> reportPost({
    required int postId,
    required String reason,
    String? description,
  }) async {
    await _setStoredToken();

    await _post(
      '/social/posts/$postId/report',
      data: {'reason': reason, 'description': description},
    );
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw SocialApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (e) {
      throw SocialApiException(_mapDioError(e));
    }
  }

  ApiError _mapDioError(DioException e) {
    final data = e.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: e.message ?? 'Network error',
      traceId: e.response?.headers.value('x-trace-id'),
    );
  }
}
