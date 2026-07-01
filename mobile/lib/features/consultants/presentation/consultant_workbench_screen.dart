import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
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

    return Scaffold(
      appBar: const FarmAppBar(title: 'میزکار مشاور'),
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
                              state.requests.isEmpty
                                  ? ListView(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      SizedBox(height: r.v(120)),
                                      const FarmEmptyView(
                                        message:
                                            'درخواست ارجاع‌شده‌ای برای شما وجود ندارد.',
                                      ),
                                    ],
                                  )
                                  : ListView.separated(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: state.requests.length,
                                    separatorBuilder:
                                        (_, __) => SizedBox(height: r.v(10)),
                                    itemBuilder: (context, index) {
                                      final request = state.requests[index];
                                      return _AssignedRequestCard(
                                        request: request,
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

class _StatusFilterChips extends StatelessWidget {
  const _StatusFilterChips({
    required this.selectedStatus,
    required this.onSelected,
  });

  final String? selectedStatus;
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
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          Padding(
            padding: const EdgeInsetsDirectional.only(end: 8),
            child: ChoiceChip(
              label: const Text('همه'),
              selected: selectedStatus == null,
              onSelected: (_) => onSelected(null),
            ),
          ),
          ...statuses.map(
            (status) => Padding(
              padding: const EdgeInsetsDirectional.only(end: 8),
              child: ChoiceChip(
                label: Text(_statusLabel(status)),
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
    required this.onChangeStatus,
  });

  final ConsultationRequestModel request;
  final VoidCallback? onChangeStatus;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final subtitleParts = [
      if (request.specialty?.title.trim().isNotEmpty == true)
        request.specialty!.title,
      _contactMethodLabel(request.contactMethod),
    ];

    return Card(
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
                    _compactDate(request.createdAt),
                    style: theme.textTheme.bodySmall,
                  ),
                ),
                if (onChangeStatus != null)
                  TextButton.icon(
                    onPressed: onChangeStatus,
                    icon: const Icon(Icons.tune_outlined),
                    label: const Text('مدیریت'),
                  ),
              ],
            ),
          ],
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

String _compactDate(String value) {
  if (value.length < 10) return toPersianDigits(value);
  return toPersianDigits(value.substring(0, 10));
}
