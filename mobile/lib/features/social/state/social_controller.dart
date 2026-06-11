import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/social_api.dart';
import '../data/social_repository.dart';
import 'social_state.dart';

final socialControllerProvider =
    StateNotifierProvider<SocialController, SocialState>((ref) {
      return SocialController(repository: ref.watch(socialRepositoryProvider));
    });

class SocialController extends StateNotifier<SocialState> {
  SocialController({required SocialRepository repository})
    : _repository = repository,
      super(SocialState.initial());

  final SocialRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final categories = await _repository.categories();
      final posts = await _repository.posts();

      state = state.copyWith(
        isLoading: false,
        categories: categories,
        posts: posts,
      );
    } on SocialApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت پست‌های اجتماعی',
      );
    }
  }

  Future<void> filterByCategory(int? categoryId) async {
    state = state.copyWith(
      isSaving: true,
      selectedCategoryId: categoryId,
      clearError: true,
    );

    try {
      final posts = await _repository.posts(categoryId: categoryId);

      state = state.copyWith(isSaving: false, posts: posts);
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در فیلتر پست‌ها',
      );
    }
  }

  Future<void> loadPost(int postId) async {
    state = state.copyWith(
      isSaving: true,
      clearSelectedPost: true,
      comments: const [],
      clearError: true,
    );

    try {
      final post = await _repository.postDetail(postId);
      final comments = await _repository.comments(postId);

      state = state.copyWith(
        isSaving: false,
        selectedPost: post,
        comments: comments,
      );
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات پست',
      );
    }
  }

  Future<void> createPost({
    required int? categoryId,
    required String title,
    required String body,
    required String postType,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.createPost(
        categoryId: categoryId,
        title: title,
        body: body,
        postType: postType,
      );

      final posts = await _repository.posts(
        categoryId: state.selectedCategoryId,
      );

      state = state.copyWith(isSaving: false, posts: posts);
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در ساخت پست');
    }
  }

  Future<void> createComment({
    required int postId,
    required String body,
    int? parentCommentId,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.createComment(
        postId: postId,
        body: body,
        parentCommentId: parentCommentId,
      );

      final post = await _repository.postDetail(postId);
      final comments = await _repository.comments(postId);

      state = state.copyWith(
        isSaving: false,
        selectedPost: post,
        comments: comments,
      );
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در ثبت کامنت');
    }
  }

  Future<void> likePost(int postId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.reactToPost(postId: postId);
      await loadPost(postId);
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در ثبت واکنش');
    }
  }

  Future<void> bookmarkPost(int postId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.bookmarkPost(postId);
      state = state.copyWith(isSaving: false);
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در ذخیره پست');
    }
  }

  Future<void> reportPost(int postId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.reportPost(
        postId: postId,
        reason: 'spam',
        description: 'گزارش از اپلیکیشن موبایل',
      );

      state = state.copyWith(isSaving: false);
    } on SocialApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(isSaving: false, errorMessage: 'خطا در گزارش پست');
    }
  }
}
