import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_social_api.dart';
import '../data/admin_social_repository.dart';
import 'admin_social_state.dart';

final adminSocialControllerProvider =
    StateNotifierProvider<AdminSocialController, AdminSocialState>((ref) {
      return AdminSocialController(
        repository: ref.watch(adminSocialRepositoryProvider),
      );
    });

class AdminSocialController extends StateNotifier<AdminSocialState> {
  AdminSocialController({required AdminSocialRepository repository})
    : _repository = repository,
      super(AdminSocialState.initial());

  final AdminSocialRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final reports = await _repository.reports(
        status: state.reportStatusFilter,
      );
      final posts = await _repository.posts(status: state.postStatusFilter);
      final comments = await _repository.comments(
        status: state.commentStatusFilter,
      );

      state = state.copyWith(
        isLoading: false,
        reports: reports,
        posts: posts,
        comments: comments,
      );
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اطلاعات مدیریت اجتماعی',
      );
    }
  }

  Future<void> setReportStatusFilter(String? status) async {
    state = state.copyWith(reportStatusFilter: status, clearError: true);
    await load();
  }

  Future<void> setPostStatusFilter(String? status) async {
    state = state.copyWith(postStatusFilter: status, clearError: true);
    await load();
  }

  Future<void> setCommentStatusFilter(String? status) async {
    state = state.copyWith(commentStatusFilter: status, clearError: true);
    await load();
  }

  Future<void> updateReportStatus({
    required int reportId,
    required String status,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.updateReportStatus(reportId: reportId, status: status);
      await load();
      state = state.copyWith(isSaving: false);
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت گزارش',
      );
    }
  }

  Future<void> hidePost(int postId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.hidePost(
        postId: postId,
        reason: 'admin panel moderation',
      );
      await load();
      state = state.copyWith(isSaving: false);
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در مخفی کردن پست',
      );
    }
  }

  Future<void> unhidePost(int postId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.unhidePost(
        postId: postId,
        reason: 'admin panel moderation',
      );
      await load();
      state = state.copyWith(isSaving: false);
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در بازگردانی پست',
      );
    }
  }

  Future<void> hideComment(int commentId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.hideComment(
        commentId: commentId,
        reason: 'admin panel moderation',
      );
      await load();
      state = state.copyWith(isSaving: false);
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در مخفی کردن کامنت',
      );
    }
  }

  Future<void> unhideComment(int commentId) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.unhideComment(
        commentId: commentId,
        reason: 'admin panel moderation',
      );
      await load();
      state = state.copyWith(isSaving: false);
    } on AdminSocialApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در بازگردانی کامنت',
      );
    }
  }
}
