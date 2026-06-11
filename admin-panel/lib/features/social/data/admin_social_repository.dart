import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_social_api.dart';
import 'admin_social_models.dart';

final adminSocialRepositoryProvider = Provider<AdminSocialRepository>((ref) {
  return AdminSocialRepository(api: AdminSocialApi());
});

class AdminSocialRepository {
  AdminSocialRepository({required AdminSocialApi api}) : _api = api;

  final AdminSocialApi _api;

  Future<List<AdminSocialReport>> reports({
    String? status,
    String? targetType,
  }) {
    return _api.reports(status: status, targetType: targetType);
  }

  Future<AdminSocialReport> updateReportStatus({
    required int reportId,
    required String status,
  }) {
    return _api.updateReportStatus(reportId: reportId, status: status);
  }

  Future<List<AdminSocialPost>> posts({String? status, String? postType}) {
    return _api.posts(status: status, postType: postType);
  }

  Future<AdminSocialPost> hidePost({required int postId, String? reason}) {
    return _api.hidePost(postId: postId, reason: reason);
  }

  Future<AdminSocialPost> unhidePost({required int postId, String? reason}) {
    return _api.unhidePost(postId: postId, reason: reason);
  }

  Future<List<AdminSocialComment>> comments({String? status, int? postId}) {
    return _api.comments(status: status, postId: postId);
  }

  Future<AdminSocialComment> hideComment({
    required int commentId,
    String? reason,
  }) {
    return _api.hideComment(commentId: commentId, reason: reason);
  }

  Future<AdminSocialComment> unhideComment({
    required int commentId,
    String? reason,
  }) {
    return _api.unhideComment(commentId: commentId, reason: reason);
  }
}
