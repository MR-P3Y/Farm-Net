import '../data/admin_social_models.dart';

const _unset = Object();

class AdminSocialState {
  const AdminSocialState({
    required this.isLoading,
    this.isSaving = false,
    this.reports = const [],
    this.posts = const [],
    this.comments = const [],
    this.reportStatusFilter,
    this.postStatusFilter,
    this.commentStatusFilter,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;

  final List<AdminSocialReport> reports;
  final List<AdminSocialPost> posts;
  final List<AdminSocialComment> comments;

  final String? reportStatusFilter;
  final String? postStatusFilter;
  final String? commentStatusFilter;

  final String? errorMessage;

  factory AdminSocialState.initial() {
    return const AdminSocialState(isLoading: true);
  }

  AdminSocialState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminSocialReport>? reports,
    List<AdminSocialPost>? posts,
    List<AdminSocialComment>? comments,
    Object? reportStatusFilter = _unset,
    Object? postStatusFilter = _unset,
    Object? commentStatusFilter = _unset,
    String? errorMessage,
    bool clearError = false,
  }) {
    return AdminSocialState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      reports: reports ?? this.reports,
      posts: posts ?? this.posts,
      comments: comments ?? this.comments,
      reportStatusFilter:
          identical(reportStatusFilter, _unset)
              ? this.reportStatusFilter
              : reportStatusFilter as String?,
      postStatusFilter:
          identical(postStatusFilter, _unset)
              ? this.postStatusFilter
              : postStatusFilter as String?,
      commentStatusFilter:
          identical(commentStatusFilter, _unset)
              ? this.commentStatusFilter
              : commentStatusFilter as String?,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
