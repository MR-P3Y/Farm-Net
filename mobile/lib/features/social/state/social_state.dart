import '../data/social_models.dart';

const _unset = Object();

class SocialState {
  const SocialState({
    required this.isLoading,
    this.isSaving = false,
    this.categories = const [],
    this.posts = const [],
    this.selectedPost,
    this.comments = const [],
    this.selectedCategoryId,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;

  final List<SocialCategoryModel> categories;
  final List<SocialPostModel> posts;
  final SocialPostModel? selectedPost;
  final List<SocialCommentModel> comments;

  final int? selectedCategoryId;
  final String? errorMessage;

  factory SocialState.initial() {
    return const SocialState(isLoading: true);
  }

  SocialState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<SocialCategoryModel>? categories,
    List<SocialPostModel>? posts,
    SocialPostModel? selectedPost,
    List<SocialCommentModel>? comments,
    Object? selectedCategoryId = _unset,
    String? errorMessage,
    bool clearSelectedPost = false,
    bool clearError = false,
  }) {
    return SocialState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      categories: categories ?? this.categories,
      posts: posts ?? this.posts,
      selectedPost:
          clearSelectedPost ? null : selectedPost ?? this.selectedPost,
      comments: comments ?? this.comments,
      selectedCategoryId:
          identical(selectedCategoryId, _unset)
              ? this.selectedCategoryId
              : selectedCategoryId as int?,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
