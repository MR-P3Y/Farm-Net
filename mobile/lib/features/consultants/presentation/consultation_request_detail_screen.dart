import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/consultant_models.dart';
import '../state/consultant_request_detail_controller.dart';

class ConsultationRequestDetailScreen extends ConsumerStatefulWidget {
  const ConsultationRequestDetailScreen({
    super.key,
    required this.requestId,
    required this.assignedMode,
  });

  final int requestId;
  final bool assignedMode;

  @override
  ConsumerState<ConsultationRequestDetailScreen> createState() =>
      _ConsultationRequestDetailScreenState();
}

class _ConsultationRequestDetailScreenState
    extends ConsumerState<ConsultationRequestDetailScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref
          .read(consultantRequestDetailControllerProvider.notifier)
          .load(requestId: widget.requestId, assigned: widget.assignedMode);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantRequestDetailControllerProvider);
    final request = state.request;

    return Scaffold(
      appBar: FarmAppBar(
        title: widget.assignedMode ? 'جزئیات کار مشاور' : 'جزئیات درخواست',
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
                child: RefreshIndicator(
                  onRefresh:
                      () => ref
                          .read(
                            consultantRequestDetailControllerProvider.notifier,
                          )
                          .load(
                            requestId: widget.requestId,
                            assigned: widget.assignedMode,
                          ),
                  child: ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: r.pagePadding(),
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
                      if (request == null)
                        const _EmptyDetail()
                      else ...[
                        _RequestSummaryCard(request: request),
                        SizedBox(height: r.v(12)),
                        _RequestNotesCard(request: request),
                        SizedBox(height: r.v(12)),
                        _StatusTimelineCard(logs: request.statusLogs),
                        SizedBox(height: r.v(16)),
                        _ActionBar(
                          request: request,
                          assignedMode: widget.assignedMode,
                          isSaving: state.isSaving,
                          onCancel: () => _confirmCancel(request),
                          onChangeStatus: () => _changeStatus(request),
                        ),
                      ],
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
        .read(consultantRequestDetailControllerProvider.notifier)
        .cancelRequest(request.id);
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
        .read(consultantRequestDetailControllerProvider.notifier)
        .updateAssignedStatus(requestId: request.id, status: status);
  }
}

class _RequestSummaryCard extends StatelessWidget {
  const _RequestSummaryCard({required this.request});

  final ConsultationRequestModel request;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final consultantName = request.consultant?.resolvedName;
    final rows = [
      if (consultantName != null && consultantName.trim().isNotEmpty)
        ('مشاور', consultantName),
      if (request.specialty?.title.trim().isNotEmpty == true)
        ('تخصص', request.specialty!.title),
      ('روش ارتباط', _contactMethodLabel(request.contactMethod)),
      ('ثبت', _compactDate(request.createdAt)),
      if (request.scheduledAt != null)
        ('زمان پیشنهادی', _compactDate(request.scheduledAt!)),
      if (request.budgetAmount != null)
        (
          'بودجه',
          '${toPersianDigits(request.budgetAmount!)} ${request.currency}',
        ),
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(request.title, style: theme.textTheme.titleLarge),
                ),
                const SizedBox(width: 8),
                _StatusChip(status: request.status),
              ],
            ),
            const SizedBox(height: 12),
            Text(request.description),
            const SizedBox(height: 14),
            ...rows.map(
              (row) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _InfoRow(label: row.$1, value: row.$2),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RequestNotesCard extends StatelessWidget {
  const _RequestNotesCard({required this.request});

  final ConsultationRequestModel request;

  @override
  Widget build(BuildContext context) {
    final notes = [
      if (request.consultantNote != null &&
          request.consultantNote!.trim().isNotEmpty)
        ('یادداشت مشاور', request.consultantNote!),
      if (request.cancelReason != null &&
          request.cancelReason!.trim().isNotEmpty)
        ('دلیل لغو', request.cancelReason!),
      if (request.acceptedAt != null)
        ('پذیرش', _compactDate(request.acceptedAt!)),
      if (request.completedAt != null)
        ('تکمیل', _compactDate(request.completedAt!)),
      if (request.cancelledAt != null)
        ('لغو', _compactDate(request.cancelledAt!)),
    ];

    if (notes.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('یادداشت‌ها', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            ...notes.map(
              (row) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _InfoRow(label: row.$1, value: row.$2),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusTimelineCard extends StatelessWidget {
  const _StatusTimelineCard({required this.logs});

  final List<ConsultRequestStatusLogModel> logs;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'تاریخچه وضعیت',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            if (logs.isEmpty)
              const Text('تغییر وضعیتی ثبت نشده است.')
            else
              ...logs.map((log) => _TimelineRow(log: log)),
          ],
        ),
      ),
    );
  }
}

class _TimelineRow extends StatelessWidget {
  const _TimelineRow({required this.log});

  final ConsultRequestStatusLogModel log;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final change = [
      if (log.fromStatus != null) _statusLabel(log.fromStatus!),
      _statusLabel(log.toStatus),
    ].join(' ← ');

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 20,
            color: theme.colorScheme.primary,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(change, style: theme.textTheme.bodyMedium),
                const SizedBox(height: 4),
                Text(
                  _compactDate(log.createdAt),
                  style: theme.textTheme.bodySmall,
                ),
                if (log.note != null && log.note!.trim().isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(log.note!, style: theme.textTheme.bodySmall),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionBar extends StatelessWidget {
  const _ActionBar({
    required this.request,
    required this.assignedMode,
    required this.isSaving,
    required this.onCancel,
    required this.onChangeStatus,
  });

  final ConsultationRequestModel request;
  final bool assignedMode;
  final bool isSaving;
  final VoidCallback onCancel;
  final VoidCallback onChangeStatus;

  @override
  Widget build(BuildContext context) {
    if (assignedMode) {
      if (!request.canConsultantManage) return const SizedBox.shrink();

      return FilledButton.icon(
        onPressed: isSaving ? null : onChangeStatus,
        icon: const Icon(Icons.tune_outlined),
        label: const Text('مدیریت وضعیت'),
      );
    }

    if (!request.canCancel) return const SizedBox.shrink();

    return OutlinedButton.icon(
      onPressed: isSaving ? null : onCancel,
      icon: const Icon(Icons.cancel_outlined),
      label: const Text('لغو درخواست'),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 92,
          child: Text(label, style: theme.textTheme.bodySmall),
        ),
        const SizedBox(width: 8),
        Expanded(child: Text(value)),
      ],
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

class _EmptyDetail extends StatelessWidget {
  const _EmptyDetail();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Text('درخواست مشاوره پیدا نشد.'),
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
