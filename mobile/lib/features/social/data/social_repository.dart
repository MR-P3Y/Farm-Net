import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'social_api.dart';
import 'social_models.dart';

final socialRepositoryProvider = Provider<SocialRepository>((ref) {
  return SocialRepository(api: SocialApi());
});

class SocialRepository {
  SocialRepository({required SocialApi api}) : _api = api;

  final SocialApi _api;

  Future<List<SocialCategoryModel>> categories() => _api.categories();

  Future<List<SocialPostModel>> posts({
    int? categoryId,
    String? postType,
    String? query,
  }) {
    return _api.posts(categoryId: categoryId, postType: postType, query: query);
  }

  Future<SocialPostModel> postDetail(int postId) => _api.postDetail(postId);

  Future<SocialPostModel> createPost({
    required int? categoryId,
    required String title,
    required String body,
    required String postType,
    int? mediaFileId,
  }) {
    return _api.createPost(
      categoryId: categoryId,
      title: title,
      body: body,
      postType: postType,
      mediaFileId: mediaFileId,
    );
  }

  Future<List<SocialCommentModel>> comments(int postId) =>
      _api.comments(postId);

  Future<SocialCommentModel> createComment({
    required int postId,
    required String body,
    int? parentCommentId,
  }) {
    return _api.createComment(
      postId: postId,
      body: body,
      parentCommentId: parentCommentId,
    );
  }

  Future<void> reactToPost({
    required int postId,
    String reactionType = 'like',
  }) {
    return _api.reactToPost(postId: postId, reactionType: reactionType);
  }

  Future<void> bookmarkPost(int postId) => _api.bookmarkPost(postId);

  Future<void> reportPost({
    required int postId,
    required String reason,
    String? description,
  }) {
    return _api.reportPost(
      postId: postId,
      reason: reason,
      description: description,
    );
  }
}
