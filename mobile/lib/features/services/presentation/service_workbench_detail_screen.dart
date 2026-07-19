import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../data/service_models.dart';
import '../state/service_workbench_controller.dart';

class ServiceWorkbenchDetailScreen extends ConsumerStatefulWidget {
  const ServiceWorkbenchDetailScreen({required this.requestId, super.key});
  final int requestId;
  @override
  ConsumerState<ServiceWorkbenchDetailScreen> createState() => _State();
}

class _State extends ConsumerState<ServiceWorkbenchDetailScreen> {
  bool _loaded = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref
          .read(serviceWorkbenchProvider.notifier)
          .loadDetail(widget.requestId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(serviceWorkbenchProvider);
    final q = s.selected?.id == widget.requestId ? s.selected : null;
    return Scaffold(
      appBar: AppBar(title: const Text('جزئیات کار خدمت')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (s.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return RefreshIndicator(
            onRefresh:
                () => ref
                    .read(serviceWorkbenchProvider.notifier)
                    .loadDetail(widget.requestId),
            child: ListView(
              padding: r.pagePadding(),
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                if (s.isSaving) const LinearProgressIndicator(),
                if (s.errorMessage != null)
                  Text(
                    s.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (s.successMessage != null)
                  Text(
                    s.successMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                if (q == null)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(40),
                      child: Text('درخواست پیدا نشد.'),
                    ),
                  )
                else ...[
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  q.title,
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                              ),
                              Chip(label: Text(q.statusLabelFa)),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(q.description ?? ''),
                          const Divider(height: 28),
                          _Info('خدمت', q.offerTitle ?? '-'),
                          _Info('دسته', q.categoryTitle ?? '-'),
                          _Info(
                            'درخواست‌دهنده',
                            'شناسه ${q.requesterUserId ?? '-'}',
                          ),
                          _Info('روش ارتباط', _contact(q.contactMethod)),
                          if (q.scheduledAt != null)
                            _Info('زمان پیشنهادی', q.scheduledAt!),
                          if (q.budgetAmount != null)
                            _Info(
                              'بودجه',
                              '${q.budgetAmount!.toStringAsFixed(0)} ${q.currency == 'TOMAN' ? 'تومان' : q.currency}',
                            ),
                          if ([
                            q.provinceName,
                            q.cityName,
                          ].any((v) => v?.isNotEmpty ?? false))
                            _Info(
                              'موقعیت',
                              [
                                q.provinceName,
                                q.cityName,
                              ].whereType<String>().join('، '),
                            ),
                          if ((q.addressText ?? '').isNotEmpty)
                            _Info('نشانی', q.addressText!),
                          if ((q.providerNote ?? '').isNotEmpty)
                            _Info('یادداشت شما', q.providerNote!),
                          if ((q.cancelReason ?? '').isNotEmpty)
                            _Info('دلیل لغو', q.cancelReason!),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _Timeline(logs: q.statusLogs),
                  const SizedBox(height: 16),
                  ...q.providerNextStatuses.map(
                    (status) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: FilledButton(
                        onPressed:
                            s.isSaving ? null : () => _confirm(q, status),
                        child: Text(_action(status)),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _confirm(ServiceRequest q, String status) async {
    final note = TextEditingController();
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (c) => AlertDialog(
            title: Text(_action(status)),
            content: TextField(
              controller: note,
              decoration: const InputDecoration(labelText: 'یادداشت — اختیاری'),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: const Text('تأیید'),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref
          .read(serviceWorkbenchProvider.notifier)
          .update(q.id, status, note: note.text);
    }
    note.dispose();
  }
}

class _Info extends StatelessWidget {
  const _Info(this.label, this.value);
  final String label, value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 5),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 125, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}

class _Timeline extends StatelessWidget {
  const _Timeline({required this.logs});
  final List<ServiceRequestStatusLog> logs;
  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('تاریخچه وضعیت', style: Theme.of(context).textTheme.titleMedium),
          if (logs.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text('تغییری ثبت نشده است.'),
            )
          else
            ...logs.map(
              (log) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.circle, size: 12),
                title: Text(
                  '${log.oldStatus == null ? 'شروع' : requestStatusLabel(log.oldStatus!)} ← ${requestStatusLabel(log.newStatus)}',
                ),
                subtitle: Text(
                  [
                    log.createdAt,
                    if ((log.note ?? '').isNotEmpty) log.note!,
                  ].join(' • '),
                ),
              ),
            ),
        ],
      ),
    ),
  );
}

String _contact(String? m) =>
    const {
      'in_app': 'داخل اپلیکیشن',
      'phone': 'تلفنی',
      'video': 'تصویری',
      'visit': 'حضوری',
    }[m] ??
    '-';
String _action(String s) =>
    const {
      'accepted': 'پذیرش درخواست',
      'rejected': 'رد درخواست',
      'in_progress': 'شروع انجام خدمت',
      'completed': 'تکمیل خدمت',
    }[s] ??
    s;
