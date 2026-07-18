import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_social_models.dart';
import '../state/admin_social_controller.dart';

class AdminSocialPage extends ConsumerStatefulWidget {
  const AdminSocialPage({super.key});

  @override
  ConsumerState<AdminSocialPage> createState() => _AdminSocialPageState();
}

class _AdminSocialPageState extends ConsumerState<AdminSocialPage> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminSocialControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminSocialControllerProvider);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return Padding(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    'مدیریت جامعه',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  OutlinedButton.icon(
                    onPressed: () => context.go('/social-categories'),
                    icon: const Icon(Icons.category_outlined),
                    label: const Text('دسته‌بندی‌ها'),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    tooltip: 'Refresh',
                    onPressed:
                        state.isSaving
                            ? null
                            : () =>
                                ref
                                    .read(
                                      adminSocialControllerProvider.notifier,
                                    )
                                    .load(),
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              if (state.isSaving) ...[
                const SizedBox(height: 12),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 16),
              Expanded(
                child:
                    state.isLoading
                        ? const AdminLoadingView()
                        : DefaultTabController(
                          length: 3,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              const TabBar(
                                tabs: [
                                  Tab(text: 'گزارش‌ها'),
                                  Tab(text: 'پست‌ها'),
                                  Tab(text: 'کامنت‌ها'),
                                ],
                              ),
                              const SizedBox(height: 16),
                              Expanded(
                                child: TabBarView(
                                  children: [
                                    _ReportsTab(
                                      reports: state.reports,
                                      statusFilter: state.reportStatusFilter,
                                      isSaving: state.isSaving,
                                    ),
                                    _PostsTab(
                                      posts: state.posts,
                                      statusFilter: state.postStatusFilter,
                                      isSaving: state.isSaving,
                                    ),
                                    _CommentsTab(
                                      comments: state.comments,
                                      statusFilter: state.commentStatusFilter,
                                      isSaving: state.isSaving,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ReportsTab extends ConsumerWidget {
  const _ReportsTab({
    required this.reports,
    required this.statusFilter,
    required this.isSaving,
  });

  final List<AdminSocialReport> reports;
  final String? statusFilter;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        _TabToolbar(
          title: 'گزارش‌ها',
          count: reports.length,
          child: _StatusFilter(
            label: 'Status',
            value: statusFilter,
            statuses: const ['open', 'reviewed', 'dismissed', 'action_taken'],
            onChanged:
                (status) => ref
                    .read(adminSocialControllerProvider.notifier)
                    .setReportStatusFilter(status),
          ),
        ),
        const SizedBox(height: 12),
        if (reports.isEmpty)
          const AdminEmptyView(message: 'گزارشی وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('Target')),
              DataColumn(label: Text('Reason')),
              DataColumn(label: Text('Status')),
              DataColumn(label: Text('Post')),
              DataColumn(label: Text('Comment')),
              DataColumn(label: Text('Action')),
            ],
            rows:
                reports.map((report) {
                  return DataRow(
                    cells: [
                      DataCell(Text(report.id.toString())),
                      DataCell(Text(report.targetType)),
                      DataCell(Text(report.reason)),
                      DataCell(Text(report.status)),
                      DataCell(Text(report.postId?.toString() ?? '-')),
                      DataCell(Text(report.commentId?.toString() ?? '-')),
                      DataCell(
                        _ReportStatusActions(
                          report: report,
                          isSaving: isSaving,
                        ),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }
}

class _PostsTab extends ConsumerWidget {
  const _PostsTab({
    required this.posts,
    required this.statusFilter,
    required this.isSaving,
  });

  final List<AdminSocialPost> posts;
  final String? statusFilter;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        _TabToolbar(
          title: 'پست‌ها',
          count: posts.length,
          child: _StatusFilter(
            label: 'Status',
            value: statusFilter,
            statuses: const [
              'draft',
              'published',
              'hidden',
              'deleted',
              'rejected',
            ],
            onChanged:
                (status) => ref
                    .read(adminSocialControllerProvider.notifier)
                    .setPostStatusFilter(status),
          ),
        ),
        const SizedBox(height: 12),
        if (posts.isEmpty)
          const AdminEmptyView(message: 'پستی وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('Title')),
              DataColumn(label: Text('Type')),
              DataColumn(label: Text('Status')),
              DataColumn(label: Text('Comments')),
              DataColumn(label: Text('Reports')),
              DataColumn(label: Text('Action')),
            ],
            rows:
                posts.map((post) {
                  return DataRow(
                    cells: [
                      DataCell(Text(post.id.toString())),
                      DataCell(
                        SizedBox(
                          width: 260,
                          child: Text(
                            post.title,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      DataCell(Text(post.postType)),
                      DataCell(Text(post.status)),
                      DataCell(Text(post.commentsCount.toString())),
                      DataCell(Text(post.reportsCount.toString())),
                      DataCell(
                        _PostModerationAction(post: post, isSaving: isSaving),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }
}

class _CommentsTab extends ConsumerWidget {
  const _CommentsTab({
    required this.comments,
    required this.statusFilter,
    required this.isSaving,
  });

  final List<AdminSocialComment> comments;
  final String? statusFilter;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        _TabToolbar(
          title: 'کامنت‌ها',
          count: comments.length,
          child: _StatusFilter(
            label: 'Status',
            value: statusFilter,
            statuses: const ['published', 'hidden', 'deleted', 'rejected'],
            onChanged:
                (status) => ref
                    .read(adminSocialControllerProvider.notifier)
                    .setCommentStatusFilter(status),
          ),
        ),
        const SizedBox(height: 12),
        if (comments.isEmpty)
          const AdminEmptyView(message: 'کامنتی وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('Post')),
              DataColumn(label: Text('Body')),
              DataColumn(label: Text('Status')),
              DataColumn(label: Text('Reports')),
              DataColumn(label: Text('Action')),
            ],
            rows:
                comments.map((comment) {
                  return DataRow(
                    cells: [
                      DataCell(Text(comment.id.toString())),
                      DataCell(Text(comment.postId.toString())),
                      DataCell(
                        SizedBox(
                          width: 320,
                          child: Text(
                            comment.body,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      DataCell(Text(comment.status)),
                      DataCell(Text(comment.reportsCount.toString())),
                      DataCell(
                        _CommentModerationAction(
                          comment: comment,
                          isSaving: isSaving,
                        ),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }
}

class _TabToolbar extends StatelessWidget {
  const _TabToolbar({
    required this.title,
    required this.count,
    required this.child,
  });

  final String title;
  final int count;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        Chip(label: Text('Count: $count')),
        SizedBox(width: 220, child: child),
      ],
    );
  }
}

class _StatusFilter extends StatelessWidget {
  const _StatusFilter({
    required this.label,
    required this.value,
    required this.statuses,
    required this.onChanged,
  });

  final String label;
  final String? value;
  final List<String> statuses;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      initialValue: value ?? 'all',
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
        isDense: true,
      ),
      items: [
        const DropdownMenuItem(value: 'all', child: Text('همه')),
        ...statuses.map(
          (status) => DropdownMenuItem(value: status, child: Text(status)),
        ),
      ],
      onChanged: (selected) {
        onChanged(selected == 'all' ? null : selected);
      },
    );
  }
}

class _ReportStatusActions extends ConsumerWidget {
  const _ReportStatusActions({required this.report, required this.isSaving});

  final AdminSocialReport report;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Wrap(
      spacing: 4,
      children: [
        _ReportActionButton(
          label: 'Review',
          status: 'reviewed',
          currentStatus: report.status,
          isSaving: isSaving,
          onPressed:
              () => ref
                  .read(adminSocialControllerProvider.notifier)
                  .updateReportStatus(reportId: report.id, status: 'reviewed'),
        ),
        _ReportActionButton(
          label: 'Dismiss',
          status: 'dismissed',
          currentStatus: report.status,
          isSaving: isSaving,
          onPressed:
              () => ref
                  .read(adminSocialControllerProvider.notifier)
                  .updateReportStatus(reportId: report.id, status: 'dismissed'),
        ),
        _ReportActionButton(
          label: 'Action',
          status: 'action_taken',
          currentStatus: report.status,
          isSaving: isSaving,
          onPressed:
              () => ref
                  .read(adminSocialControllerProvider.notifier)
                  .updateReportStatus(
                    reportId: report.id,
                    status: 'action_taken',
                  ),
        ),
      ],
    );
  }
}

class _ReportActionButton extends StatelessWidget {
  const _ReportActionButton({
    required this.label,
    required this.status,
    required this.currentStatus,
    required this.isSaving,
    required this.onPressed,
  });

  final String label;
  final String status;
  final String currentStatus;
  final bool isSaving;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: isSaving || currentStatus == status ? null : onPressed,
      child: Text(label),
    );
  }
}

class _PostModerationAction extends ConsumerWidget {
  const _PostModerationAction({required this.post, required this.isSaving});

  final AdminSocialPost post;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (post.status == 'hidden') {
      return TextButton(
        onPressed:
            isSaving
                ? null
                : () => ref
                    .read(adminSocialControllerProvider.notifier)
                    .unhidePost(post.id),
        child: const Text('Unhide'),
      );
    }

    if (post.status != 'published') {
      return const Text('-');
    }

    return TextButton(
      onPressed:
          isSaving
              ? null
              : () => ref
                  .read(adminSocialControllerProvider.notifier)
                  .hidePost(post.id),
      child: const Text('Hide'),
    );
  }
}

class _CommentModerationAction extends ConsumerWidget {
  const _CommentModerationAction({
    required this.comment,
    required this.isSaving,
  });

  final AdminSocialComment comment;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (comment.status == 'hidden') {
      return TextButton(
        onPressed:
            isSaving
                ? null
                : () => ref
                    .read(adminSocialControllerProvider.notifier)
                    .unhideComment(comment.id),
        child: const Text('Unhide'),
      );
    }

    if (comment.status != 'published') {
      return const Text('-');
    }

    return TextButton(
      onPressed:
          isSaving
              ? null
              : () => ref
                  .read(adminSocialControllerProvider.notifier)
                  .hideComment(comment.id),
      child: const Text('Hide'),
    );
  }
}
