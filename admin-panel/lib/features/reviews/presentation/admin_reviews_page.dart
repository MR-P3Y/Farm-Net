import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../../../core/auth/admin_auth_state.dart';
import '../data/admin_review_repository.dart';
import '../state/admin_review_controller.dart';

class AdminReviewsPage extends ConsumerStatefulWidget {
  const AdminReviewsPage({super.key});
  @override
  ConsumerState<AdminReviewsPage> createState() => _State();
}

class _State extends ConsumerState<AdminReviewsPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(adminReviewControllerProvider.notifier).load(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminReviewControllerProvider);
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'مدیریت نظرات',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                tooltip: 'تازه‌سازی',
                onPressed:
                    state.saving
                        ? null
                        : () =>
                            ref
                                .read(adminReviewControllerProvider.notifier)
                                .load(),
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          if (state.saving) const LinearProgressIndicator(),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Text(
                state.error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ),
          const SizedBox(height: 12),
          Expanded(
            child:
                state.loading
                    ? const AdminLoadingView()
                    : DefaultTabController(
                      length: 2,
                      child: Column(
                        children: [
                          const TabBar(
                            tabs: [Tab(text: 'نظرات'), Tab(text: 'گزارش‌ها')],
                          ),
                          const SizedBox(height: 12),
                          Expanded(
                            child: TabBarView(
                              children: [
                                _ReviewsTab(state: state),
                                _ReportsTab(state: state),
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
  }
}

class _ReviewsTab extends ConsumerWidget {
  const _ReviewsTab({required this.state});
  final AdminReviewState state;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final canModerate = ref
        .watch(adminAuthStateProvider)
        .hasPermission('reviews.admin_moderate');
    return ListView(
      children: [
        _Filter(
          value: state.reviewStatus,
          values: const ['active', 'hidden', 'deleted'],
          onChanged:
              ref.read(adminReviewControllerProvider.notifier).filterReviews,
        ),
        const SizedBox(height: 12),
        if (state.reviews.isEmpty)
          const AdminEmptyView(message: 'نظری وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('موضوع')),
              DataColumn(label: Text('امتیاز')),
              DataColumn(label: Text('متن')),
              DataColumn(label: Text('وضعیت')),
              DataColumn(label: Text('عملیات')),
            ],
            rows:
                state.reviews
                    .map(
                      (row) => DataRow(
                        cells: [
                          DataCell(Text('${row.id}')),
                          DataCell(
                            Text('${row.subjectType} #${row.subjectId}'),
                          ),
                          DataCell(Text('${row.score}/5')),
                          DataCell(
                            SizedBox(
                              width: 260,
                              child: Text(
                                row.body ?? '-',
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                          DataCell(Text(row.status)),
                          DataCell(
                            Wrap(
                              children: [
                                IconButton(
                                  tooltip: 'خط زمانی ممیزی',
                                  onPressed:
                                      () => _showLogs(context, ref, row.id),
                                  icon: const Icon(Icons.history),
                                ),
                                if (canModerate)
                                  PopupMenuButton<String>(
                                    enabled:
                                        !state.saving &&
                                        row.status != 'deleted',
                                    onSelected:
                                        (status) => _moderate(
                                          context,
                                          ref,
                                          row.id,
                                          status,
                                        ),
                                    itemBuilder:
                                        (_) => [
                                          if (row.status != 'hidden')
                                            const PopupMenuItem(
                                              value: 'hidden',
                                              child: Text('مخفی‌سازی'),
                                            ),
                                          if (row.status == 'hidden')
                                            const PopupMenuItem(
                                              value: 'active',
                                              child: Text('بازیابی'),
                                            ),
                                          const PopupMenuItem(
                                            value: 'deleted',
                                            child: Text('حذف نهایی'),
                                          ),
                                        ],
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    )
                    .toList(),
          ),
        _Pager(
          page: state.reviewPage,
          pages: state.reviewPages,
          onPage: ref.read(adminReviewControllerProvider.notifier).reviewPage,
        ),
      ],
    );
  }
}

class _ReportsTab extends ConsumerWidget {
  const _ReportsTab({required this.state});
  final AdminReviewState state;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final canResolve = ref
        .watch(adminAuthStateProvider)
        .hasPermission('review_reports.admin_resolve');
    return ListView(
      children: [
        _Filter(
          value: state.reportStatus,
          values: const ['open', 'reviewed', 'resolved', 'dismissed'],
          onChanged:
              ref.read(adminReviewControllerProvider.notifier).filterReports,
        ),
        const SizedBox(height: 12),
        if (state.reports.isEmpty)
          const AdminEmptyView(message: 'گزارشی وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('نظر')),
              DataColumn(label: Text('دلیل')),
              DataColumn(label: Text('توضیح')),
              DataColumn(label: Text('وضعیت')),
              DataColumn(label: Text('عملیات')),
            ],
            rows:
                state.reports
                    .map(
                      (row) => DataRow(
                        cells: [
                          DataCell(Text('${row.id}')),
                          DataCell(Text('#${row.reviewId}')),
                          DataCell(Text(row.reason)),
                          DataCell(
                            SizedBox(
                              width: 260,
                              child: Text(
                                row.description ?? '-',
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                          DataCell(Text(row.status)),
                          DataCell(
                            canResolve
                                ? PopupMenuButton<String>(
                                  enabled:
                                      !state.saving &&
                                      !{
                                        'resolved',
                                        'dismissed',
                                      }.contains(row.status),
                                  onSelected:
                                      (status) => _resolve(
                                        context,
                                        ref,
                                        row.id,
                                        status,
                                      ),
                                  itemBuilder:
                                      (_) => const [
                                        PopupMenuItem(
                                          value: 'reviewed',
                                          child: Text('بررسی شد'),
                                        ),
                                        PopupMenuItem(
                                          value: 'resolved',
                                          child: Text('تأیید گزارش'),
                                        ),
                                        PopupMenuItem(
                                          value: 'dismissed',
                                          child: Text('رد گزارش'),
                                        ),
                                      ],
                                )
                                : const Text('فقط مشاهده'),
                          ),
                        ],
                      ),
                    )
                    .toList(),
          ),
        _Pager(
          page: state.reportPage,
          pages: state.reportPages,
          onPage: ref.read(adminReviewControllerProvider.notifier).reportPage,
        ),
      ],
    );
  }
}

Future<String?> _note(BuildContext context, String title) async {
  final controller = TextEditingController();
  final value = await showDialog<String>(
    context: context,
    builder:
        (context) => AlertDialog(
          title: Text(title),
          content: TextField(
            controller: controller,
            minLines: 2,
            maxLines: 5,
            decoration: const InputDecoration(labelText: 'یادداشت اجباری'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () {
                final note = controller.text.trim();
                if (note.length >= 2) Navigator.pop(context, note);
              },
              child: const Text('ثبت'),
            ),
          ],
        ),
  );
  controller.dispose();
  return value;
}

Future<void> _moderate(
  BuildContext context,
  WidgetRef ref,
  int id,
  String status,
) async {
  final note = await _note(context, 'تغییر وضعیت نظر');
  if (note != null) {
    await ref
        .read(adminReviewControllerProvider.notifier)
        .moderate(id, status, note);
  }
}

Future<void> _resolve(
  BuildContext context,
  WidgetRef ref,
  int id,
  String status,
) async {
  final note = await _note(context, 'نتیجه بررسی گزارش');
  if (note != null) {
    await ref
        .read(adminReviewControllerProvider.notifier)
        .resolve(id, status, note);
  }
}

Future<void> _showLogs(
  BuildContext context,
  WidgetRef ref,
  int reviewId,
) async {
  final logs = await ref.read(adminReviewRepositoryProvider).logs(reviewId);
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder:
        (context) => AlertDialog(
          title: Text('خط زمانی نظر #$reviewId'),
          content: SizedBox(
            width: 600,
            child:
                logs.isEmpty
                    ? const Text('رویدادی ثبت نشده است.')
                    : ListView(
                      shrinkWrap: true,
                      children:
                          logs
                              .map(
                                (log) => ListTile(
                                  leading: const Icon(Icons.history),
                                  title: Text(log.action),
                                  subtitle: Text(
                                    '${log.fromStatus ?? '-'} → ${log.toStatus ?? '-'}\n${log.note ?? ''}',
                                  ),
                                ),
                              )
                              .toList(),
                    ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('بستن'),
            ),
          ],
        ),
  );
}

class _Filter extends StatelessWidget {
  const _Filter({
    required this.value,
    required this.values,
    required this.onChanged,
  });
  final String? value;
  final List<String> values;
  final ValueChanged<String?> onChanged;
  @override
  Widget build(BuildContext context) => Align(
    alignment: Alignment.centerRight,
    child: SizedBox(
      width: 240,
      child: DropdownButtonFormField<String>(
        initialValue: value ?? 'all',
        decoration: const InputDecoration(labelText: 'فیلتر وضعیت'),
        items: [
          const DropdownMenuItem(value: 'all', child: Text('همه')),
          ...values.map((e) => DropdownMenuItem(value: e, child: Text(e))),
        ],
        onChanged: (value) => onChanged(value == 'all' ? null : value),
      ),
    ),
  );
}

class _Pager extends StatelessWidget {
  const _Pager({required this.page, required this.pages, required this.onPage});
  final int page;
  final int pages;
  final ValueChanged<int> onPage;
  @override
  Widget build(BuildContext context) => Row(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      IconButton(
        onPressed: page > 1 ? () => onPage(page - 1) : null,
        icon: const Icon(Icons.chevron_right),
      ),
      Text('$page / ${pages == 0 ? 1 : pages}'),
      IconButton(
        onPressed: page < pages ? () => onPage(page + 1) : null,
        icon: const Icon(Icons.chevron_left),
      ),
    ],
  );
}
