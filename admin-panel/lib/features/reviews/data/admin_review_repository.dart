import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_review_api.dart';
import 'admin_review_models.dart';

final adminReviewRepositoryProvider = Provider(
  (ref) => AdminReviewRepository(AdminReviewApi()),
);

class AdminReviewRepository {
  AdminReviewRepository(this._api);
  final AdminReviewApi _api;
  Future<AdminReviewPage<AdminReview>> reviews({String? status, int page = 1}) =>
      _api.reviews(status: status, page: page);
  Future<AdminReviewPage<AdminReviewReport>> reports({
    String? status,
    int page = 1,
  }) => _api.reports(status: status, page: page);
  Future<List<AdminReviewLog>> logs(int id) => _api.logs(id);
  Future<void> moderate(int id, String status, String note) =>
      _api.moderateReview(id, status, note);
  Future<void> resolve(int id, String status, String note) =>
      _api.resolveReport(id, status, note);
}
