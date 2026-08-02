import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/consultant_models.dart';
import '../state/consultant_request_controller.dart';

class MyConsultationRequestsScreen extends ConsumerStatefulWidget {
  const MyConsultationRequestsScreen({super.key});

  @override
  ConsumerState<MyConsultationRequestsScreen> createState() =>
      _MyConsultationRequestsScreenState();
}

class _MyConsultationRequestsScreenState
    extends ConsumerState<MyConsultationRequestsScreen> {
  bool _loaded = false;
  String _selectedStatus = 'all';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(consultantRequestControllerProvider.notifier).loadMyRequests();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantRequestControllerProvider);
    final visibleRequests =
        _selectedStatus == 'all'
            ? state.requests
            : state.requests
                .where((request) => request.status == _selectedStatus)
                .toList();

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'درخواست‌های مشاوره من',
          en: 'My consultation requests',
        ),
        actions: [
          IconButton(
            tooltip: context.l10n.tr(fa: 'انتخاب مشاور', en: 'Find consultant'),
            onPressed: () => context.go('/consultants'),
            icon: const Icon(Icons.support_agent_outlined),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/consultants'),
        icon: const Icon(Icons.add_comment_outlined),
        label: Text(context.l10n.tr(fa: 'درخواست جدید', en: 'New request')),
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            if (state.isLoading) {
              return const FarmLoadingView();
            }

            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _RequestsOverview(requests: state.requests),
                      SizedBox(height: r.v(10)),
                      _StatusFilters(
                        selected: _selectedStatus,
                        requests: state.requests,
                        onSelected:
                            (value) => setState(() => _selectedStatus = value),
                      ),
                      if (state.isSaving) const LinearProgressIndicator(),
                      if (state.errorMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _MessageBox(
                          message: state.errorMessage!,
                          isError: true,
                        ),
                      ],
                      if (state.successMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _MessageBox(
                          message: state.successMessage!,
                          isError: false,
                        ),
                      ],
                      SizedBox(height: r.v(12)),
                      Expanded(
                        child: RefreshIndicator(
                          onRefresh:
                              () =>
                                  ref
                                      .read(
                                        consultantRequestControllerProvider
                                            .notifier,
                                      )
                                      .loadMyRequests(),
                          child:
                              visibleRequests.isEmpty
                                  ? ListView(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      SizedBox(height: r.v(120)),
                                      FarmEmptyView(
                                        message:
                                            state.requests.isEmpty
                                                ? context.l10n.tr(
                                                  fa:
                                                      'هنوز درخواست مشاوره‌ای ثبت نکرده‌اید.',
                                                  en:
                                                      'You have no consultation requests yet.',
                                                )
                                                : context.l10n.tr(
                                                  fa:
                                                      'درخواستی با این وضعیت وجود ندارد.',
                                                  en:
                                                      'No request has this status.',
                                                ),
                                      ),
                                    ],
                                  )
                                  : ListView.separated(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: visibleRequests.length,
                                    separatorBuilder:
                                        (_, __) => SizedBox(height: r.v(10)),
                                    itemBuilder: (context, index) {
                                      final request = visibleRequests[index];
                                      return _RequestCard(
                                        request: request,
                                        onTap:
                                            () => context.push(
                                              '/consultants/requests/${request.id}',
                                            ),
                                        onCancel:
                                            request.canCancel && !state.isSaving
                                                ? () => _confirmCancel(request)
                                                : null,
                                      );
                                    },
                                  ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _confirmCancel(ConsultationRequestModel request) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('لغو درخواست'),
          content: Text('درخواست «${request.title}» لغو شود؟'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('لغو درخواست'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    await ref
        .read(consultantRequestControllerProvider.notifier)
        .cancelRequest(request.id);
  }
}

class _RequestsOverview extends StatelessWidget {
  const _RequestsOverview({required this.requests});
  final List<ConsultationRequestModel> requests;

  @override
  Widget build(BuildContext context) {
    final active =
        requests
            .where(
              (item) => const {
                'open',
                'accepted',
                'in_progress',
              }.contains(item.status),
            )
            .length;
    final completed =
        requests.where((item) => item.status == 'completed').length;
    return FarmGlassCard(
      borderRadius: 22,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        children: [
          _OverviewMetric(
            icon: Icons.all_inbox_outlined,
            value: requests.length,
            label: context.l10n.tr(fa: 'همه', en: 'All'),
          ),
          const _MetricDivider(),
          _OverviewMetric(
            icon: Icons.pending_actions_outlined,
            value: active,
            label: context.l10n.tr(fa: 'فعال', en: 'Active'),
          ),
          const _MetricDivider(),
          _OverviewMetric(
            icon: Icons.task_alt_rounded,
            value: completed,
            label: context.l10n.tr(fa: 'تکمیل', en: 'Done'),
          ),
        ],
      ),
    );
  }
}

class _OverviewMetric extends StatelessWidget {
  const _OverviewMetric({
    required this.icon,
    required this.value,
    required this.label,
  });
  final IconData icon;
  final int value;
  final String label;

  @override
  Widget build(BuildContext context) => Expanded(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 3),
        Text(
          toPersianDigits(value),
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
        ),
        Text(label, style: Theme.of(context).textTheme.labelSmall),
      ],
    ),
  );
}

class _MetricDivider extends StatelessWidget {
  const _MetricDivider();
  @override
  Widget build(BuildContext context) => SizedBox(
    height: 42,
    child: VerticalDivider(color: Theme.of(context).colorScheme.outlineVariant),
  );
}

class _StatusFilters extends StatelessWidget {
  const _StatusFilters({
    required this.selected,
    required this.requests,
    required this.onSelected,
  });
  final String selected;
  final List<ConsultationRequestModel> requests;
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    const statuses = [
      'all',
      'open',
      'accepted',
      'in_progress',
      'completed',
      'cancelled',
      'rejected',
    ];
    return SizedBox(
      height: 38,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: statuses.length,
        separatorBuilder: (_, __) => const SizedBox(width: 6),
        itemBuilder: (context, index) {
          final status = statuses[index];
          final count =
              status == 'all'
                  ? requests.length
                  : requests.where((item) => item.status == status).length;
          return ChoiceChip(
            visualDensity: VisualDensity.compact,
            selected: selected == status,
            onSelected: (_) => onSelected(status),
            label: Text(
              '${_localizedStatus(context, status)} (${toPersianDigits(count)})',
            ),
          );
        },
      ),
    );
  }
}

class _RequestCard extends StatelessWidget {
  const _RequestCard({
    required this.request,
    required this.onTap,
    required this.onCancel,
  });

  final ConsultationRequestModel request;
  final VoidCallback onTap;
  final VoidCallback? onCancel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final consultantName = request.consultant?.resolvedName;
    final subtitleParts = [
      if (consultantName != null && consultantName.trim().isNotEmpty)
        consultantName,
      if (request.specialty?.title.trim().isNotEmpty == true)
        request.specialty!.title,
      _contactMethodLabel(request.contactMethod),
    ];

    return FarmGlassCard(
      borderRadius: 22,
      padding: EdgeInsets.zero,
      child: InkWell(
        borderRadius: BorderRadius.circular(22),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      request.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleMedium,
                    ),
                  ),
                  const SizedBox(width: 8),
                  _StatusChip(status: request.status),
                ],
              ),
              if (subtitleParts.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  subtitleParts.join(' • '),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const SizedBox(height: 8),
              Text(
                request.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Icon(
                    Icons.schedule_outlined,
                    size: 18,
                    color: theme.colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      _localizedDate(context, request.createdAt),
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                  if (onCancel != null) ...[
                    TextButton.icon(
                      onPressed: onCancel,
                      icon: const Icon(Icons.cancel_outlined),
                      label: const Text('لغو'),
                    ),
                    const SizedBox(width: 4),
                  ],
                  FilledButton.tonalIcon(
                    onPressed: onTap,
                    icon: const Icon(Icons.arrow_forward_rounded, size: 18),
                    label: const Text('جزئیات'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    final color = switch (status) {
      'open' => colors.primaryContainer,
      'accepted' => colors.secondaryContainer,
      'in_progress' => colors.tertiaryContainer,
      'completed' => colors.surfaceContainerHighest,
      'cancelled' => colors.errorContainer,
      'rejected' => colors.errorContainer,
      _ => colors.surfaceContainerHighest,
    };

    return Chip(
      label: Text(_statusLabel(status)),
      backgroundColor: color,
      visualDensity: VisualDensity.compact,
    );
  }
}

class _MessageBox extends StatelessWidget {
  const _MessageBox({required this.message, required this.isError});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: isError ? colors.errorContainer : colors.primaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(
          message,
          style: TextStyle(
            color:
                isError ? colors.onErrorContainer : colors.onPrimaryContainer,
          ),
        ),
      ),
    );
  }
}

String _statusLabel(String status) {
  return switch (status) {
    'open' => 'باز',
    'accepted' => 'پذیرفته‌شده',
    'in_progress' => 'در حال انجام',
    'completed' => 'تکمیل‌شده',
    'cancelled' => 'لغوشده',
    'rejected' => 'ردشده',
    _ => status,
  };
}

String _localizedStatus(BuildContext context, String status) {
  if (context.l10n.isFa) return status == 'all' ? 'همه' : _statusLabel(status);
  return switch (status) {
    'all' => 'All',
    'open' => 'Open',
    'accepted' => 'Accepted',
    'in_progress' => 'In progress',
    'completed' => 'Completed',
    'cancelled' => 'Cancelled',
    'rejected' => 'Rejected',
    _ => status,
  };
}

String _contactMethodLabel(String method) {
  return switch (method) {
    'in_app' => 'داخل اپلیکیشن',
    'phone' => 'تلفنی',
    'video' => 'تصویری',
    'visit' => 'حضوری',
    _ => method,
  };
}

String _localizedDate(BuildContext context, String value) {
  final parsed = DateTime.tryParse(value);
  return parsed == null ? value : formatDate(context, parsed.toLocal());
}
