import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_review_api.dart';
import '../data/admin_review_models.dart';
import '../data/admin_review_repository.dart';

final adminReviewControllerProvider =
    StateNotifierProvider<AdminReviewController, AdminReviewState>(
      (ref) => AdminReviewController(ref.watch(adminReviewRepositoryProvider)),
    );

class AdminReviewState {
  const AdminReviewState({
    this.loading = true,
    this.saving = false,
    this.reviews = const [],
    this.reports = const [],
    this.reviewPage = 1,
    this.reviewPages = 0,
    this.reportPage = 1,
    this.reportPages = 0,
    this.reviewStatus,
    this.reportStatus,
    this.error,
  });
  final bool loading;
  final bool saving;
  final List<AdminReview> reviews;
  final List<AdminReviewReport> reports;
  final int reviewPage;
  final int reviewPages;
  final int reportPage;
  final int reportPages;
  final String? reviewStatus;
  final String? reportStatus;
  final String? error;

  AdminReviewState copyWith({
    bool? loading,
    bool? saving,
    List<AdminReview>? reviews,
    List<AdminReviewReport>? reports,
    int? reviewPage,
    int? reviewPages,
    int? reportPage,
    int? reportPages,
    String? reviewStatus,
    String? reportStatus,
    bool clearReviewStatus = false,
    bool clearReportStatus = false,
    String? error,
    bool clearError = false,
  }) => AdminReviewState(
    loading: loading ?? this.loading,
    saving: saving ?? this.saving,
    reviews: reviews ?? this.reviews,
    reports: reports ?? this.reports,
    reviewPage: reviewPage ?? this.reviewPage,
    reviewPages: reviewPages ?? this.reviewPages,
    reportPage: reportPage ?? this.reportPage,
    reportPages: reportPages ?? this.reportPages,
    reviewStatus: clearReviewStatus ? null : reviewStatus ?? this.reviewStatus,
    reportStatus: clearReportStatus ? null : reportStatus ?? this.reportStatus,
    error: clearError ? null : error ?? this.error,
  );
}

class AdminReviewController extends StateNotifier<AdminReviewState> {
  AdminReviewController(this._repository) : super(const AdminReviewState());
  final AdminReviewRepository _repository;

  Future<void> load() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final reviews = await _repository.reviews(
        status: state.reviewStatus,
        page: state.reviewPage,
      );
      final reports = await _repository.reports(
        status: state.reportStatus,
        page: state.reportPage,
      );
      state = state.copyWith(
        loading: false,
        reviews: reviews.items,
        reviewPage: reviews.page,
        reviewPages: reviews.totalPages,
        reports: reports.items,
        reportPage: reports.page,
        reportPages: reports.totalPages,
      );
    } on AdminReviewApiException catch (error) {
      state = state.copyWith(loading: false, error: error.error.message);
    } catch (_) {
      state = state.copyWith(
        loading: false,
        error: 'دریافت اطلاعات نظرات ناموفق بود.',
      );
    }
  }

  Future<void> filterReviews(String? status) {
    state = state.copyWith(
      reviewStatus: status,
      clearReviewStatus: status == null,
      reviewPage: 1,
    );
    return load();
  }

  Future<void> filterReports(String? status) {
    state = state.copyWith(
      reportStatus: status,
      clearReportStatus: status == null,
      reportPage: 1,
    );
    return load();
  }

  Future<void> reviewPage(int page) {
    state = state.copyWith(reviewPage: page);
    return load();
  }

  Future<void> reportPage(int page) {
    state = state.copyWith(reportPage: page);
    return load();
  }

  Future<bool> moderate(int id, String status, String note) =>
      _mutate(() => _repository.moderate(id, status, note));

  Future<bool> resolve(int id, String status, String note) =>
      _mutate(() => _repository.resolve(id, status, note));

  Future<bool> _mutate(Future<void> Function() action) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      await action();
      await load();
      state = state.copyWith(saving: false);
      return true;
    } on AdminReviewApiException catch (error) {
      state = state.copyWith(saving: false, error: error.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(saving: false, error: 'ثبت عملیات ناموفق بود.');
      return false;
    }
  }
}
