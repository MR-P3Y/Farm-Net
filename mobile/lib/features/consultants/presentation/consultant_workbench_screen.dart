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
import '../state/consultant_workbench_controller.dart';

class ConsultantWorkbenchScreen extends ConsumerStatefulWidget {
  const ConsultantWorkbenchScreen({super.key});

  @override
  ConsumerState<ConsultantWorkbenchScreen> createState() =>
      _ConsultantWorkbenchScreenState();
}

class _ConsultantWorkbenchScreenState
    extends ConsumerState<ConsultantWorkbenchScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(consultantWorkbenchControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantWorkbenchControllerProvider);
    final visibleRequests =
        state.selectedStatus == null
            ? state.requests
            : state.requests
                .where((item) => item.status == state.selectedStatus)
                .toList();

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'میزکار مشاور', en: 'Consultant workbench'),
        actions: [
          IconButton(
            tooltip: context.l10n.tr(fa: 'پروفایل من', en: 'My profile'),
            onPressed: () => context.push('/consultants/me/profile'),
            icon: const Icon(Icons.badge_outlined),
          ),
        ],
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
                      _WorkbenchOverview(requests: state.requests),
                      SizedBox(height: r.v(10)),
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
                      _StatusFilterChips(
                        selectedStatus: state.selectedStatus,
                        requests: state.requests,
                        onSelected: (status) {
                          ref
                              .read(
                                consultantWorkbenchControllerProvider.notifier,
                              )
                              .load(status: status);
                        },
                      ),
                      SizedBox(height: r.v(12)),
                      Expanded(
                        child: RefreshIndicator(
                          onRefresh:
                              () => ref
                                  .read(
                                    consultantWorkbenchControllerProvider
                                        .notifier,
                                  )
                                  .load(status: state.selectedStatus),
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
                                                      'درخواست ارجاع‌شده‌ای برای شما وجود ندارد.',
                                                  en:
                                                      'No requests are assigned to you.',
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
                                      return _AssignedRequestCard(
                                        request: request,
                                        onTap:
                                            () => context.push(
                                              '/consultants/workbench/requests/${request.id}',
                                            ),
                                        onChangeStatus:
                                            request.canConsultantManage &&
                                                    !state.isSaving
                                                ? () => _changeStatus(request)
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

  Future<void> _changeStatus(ConsultationRequestModel request) async {
    final status = await showModalBottomSheet<String>(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'تغییر وضعیت درخواست',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                ...request.consultantNextStatuses.map(
                  (status) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: FilledButton(
                      onPressed: () => Navigator.pop(context, status),
                      child: Text(_statusActionLabel(status)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (status == null) return;

    await ref
        .read(consultantWorkbenchControllerProvider.notifier)
        .updateStatus(requestId: request.id, status: status);
  }
}

class _WorkbenchOverview extends StatelessWidget {
  const _WorkbenchOverview({required this.requests});
  final List<ConsultationRequestModel> requests;

  @override
  Widget build(BuildContext context) {
    final open = requests.where((item) => item.status == 'open').length;
    final active =
        requests
            .where(
              (item) => const {'accepted', 'in_progress'}.contains(item.status),
            )
            .length;
    final completed =
        requests.where((item) => item.status == 'completed').length;
    return FarmGlassCard(
      borderRadius: 24,
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(
                Icons.support_agent_rounded,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  context.l10n.tr(
                    fa: 'مرکز مدیریت مشاوره‌ها',
                    en: 'Consultation operations',
                  ),
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _WorkbenchMetric(
                label: context.l10n.tr(fa: 'جدید', en: 'New'),
                value: open,
              ),
              const _WorkbenchDivider(),
              _WorkbenchMetric(
                label: context.l10n.tr(fa: 'فعال', en: 'Active'),
                value: active,
              ),
              const _WorkbenchDivider(),
              _WorkbenchMetric(
                label: context.l10n.tr(fa: 'تکمیل', en: 'Done'),
                value: completed,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _WorkbenchMetric extends StatelessWidget {
  const _WorkbenchMetric({required this.label, required this.value});
  final String label;
  final int value;

  @override
  Widget build(BuildContext context) => Expanded(
    child: Column(
      children: [
        Text(
          context.l10n.isFa ? toPersianDigits(value) : '$value',
          style: Theme.of(
            context,
          ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
        ),
        Text(label, style: Theme.of(context).textTheme.labelSmall),
      ],
    ),
  );
}

class _WorkbenchDivider extends StatelessWidget {
  const _WorkbenchDivider();
  @override
  Widget build(BuildContext context) => SizedBox(
    height: 36,
    child: VerticalDivider(color: Theme.of(context).colorScheme.outlineVariant),
  );
}

class _StatusFilterChips extends StatelessWidget {
  const _StatusFilterChips({
    required this.selectedStatus,
    required this.requests,
    required this.onSelected,
  });

  final String? selectedStatus;
  final List<ConsultationRequestModel> requests;
  final ValueChanged<String?> onSelected;

  @override
  Widget build(BuildContext context) {
    const statuses = [
      'open',
      'accepted',
      'in_progress',
      'completed',
      'cancelled',
      'rejected',
    ];

    return SizedBox(
      height: 38,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          Padding(
            padding: const EdgeInsetsDirectional.only(end: 8),
            child: ChoiceChip(
              visualDensity: VisualDensity.compact,
              label: Text('همه (${requests.length})'),
              selected: selectedStatus == null,
              onSelected: (_) => onSelected(null),
            ),
          ),
          ...statuses.map(
            (status) => Padding(
              padding: const EdgeInsetsDirectional.only(end: 8),
              child: ChoiceChip(
                visualDensity: VisualDensity.compact,
                label: Text(
                  '${_statusLabel(status)} (${requests.where((item) => item.status == status).length})',
                ),
                selected: selectedStatus == status,
                onSelected: (_) => onSelected(status),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AssignedRequestCard extends StatelessWidget {
  const _AssignedRequestCard({
    required this.request,
    required this.onTap,
    required this.onChangeStatus,
  });

  final ConsultationRequestModel request;
  final VoidCallback onTap;
  final VoidCallback? onChangeStatus;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final subtitleParts = [
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
                maxLines: 3,
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
                  if (onChangeStatus != null) ...[
                    TextButton.icon(
                      onPressed: onChangeStatus,
                      icon: const Icon(Icons.tune_outlined),
                      label: const Text('مدیریت'),
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

String _statusActionLabel(String status) {
  return switch (status) {
    'accepted' => 'پذیرش درخواست',
    'rejected' => 'رد درخواست',
    'in_progress' => 'شروع انجام',
    'completed' => 'تکمیل درخواست',
    'cancelled' => 'لغو درخواست',
    _ => _statusLabel(status),
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
