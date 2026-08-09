import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../data/service_models.dart';
import '../state/service_workbench_controller.dart';
import 'service_ui.dart';

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
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'جزئیات کار خدمت',
          en: 'Service job details',
        ),
        fallbackLocation: '/services/workbench',
      ),
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
                  Center(
                    child: Padding(
                      padding: EdgeInsets.all(40),
                      child: Text(
                        context.l10n.tr(
                          fa: 'درخواست پیدا نشد.',
                          en: 'Request not found.',
                        ),
                      ),
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
                              Chip(
                                label: Text(
                                  serviceRequestStatusLabel(context, q.status),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(q.description ?? ''),
                          const Divider(height: 28),
                          _Info(
                            context.l10n.tr(fa: 'خدمت', en: 'Service'),
                            q.offerTitle ?? '-',
                          ),
                          _Info(
                            context.l10n.tr(fa: 'دسته', en: 'Category'),
                            q.categoryTitle ?? '-',
                          ),
                          _Info(
                            context.l10n.tr(
                              fa: 'درخواست‌دهنده',
                              en: 'Requester',
                            ),
                            context.l10n.tr(
                              fa: 'شناسه ${q.requesterUserId ?? '-'}',
                              en: 'ID ${q.requesterUserId ?? '-'}',
                            ),
                          ),
                          _Info(
                            context.l10n.tr(
                              fa: 'روش ارتباط',
                              en: 'Contact method',
                            ),
                            serviceContactMethodLabel(context, q.contactMethod),
                          ),
                          if (q.scheduledAt != null)
                            _Info(
                              context.l10n.tr(
                                fa: 'زمان پیشنهادی',
                                en: 'Preferred date',
                              ),
                              formatApiDate(
                                context,
                                q.scheduledAt,
                                showTime: true,
                              ),
                            ),
                          if (q.budgetAmount != null)
                            _Info(
                              context.l10n.tr(fa: 'بودجه', en: 'Budget'),
                              q.currency == 'TOMAN'
                                  ? formatToman(context, q.budgetAmount!)
                                  : '${q.budgetAmount!.toStringAsFixed(0)} ${q.currency}',
                            ),
                          if ([
                            q.provinceName,
                            q.cityName,
                          ].any((v) => v?.isNotEmpty ?? false))
                            _Info(
                              context.l10n.tr(fa: 'موقعیت', en: 'Location'),
                              [
                                q.provinceName,
                                q.cityName,
                              ].whereType<String>().join('، '),
                            ),
                          if ((q.addressText ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(fa: 'نشانی', en: 'Address'),
                              q.addressText!,
                            ),
                          if ((q.providerNote ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(
                                fa: 'یادداشت شما',
                                en: 'Your note',
                              ),
                              q.providerNote!,
                            ),
                          if ((q.cancelReason ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(
                                fa: 'دلیل لغو',
                                en: 'Cancellation reason',
                              ),
                              q.cancelReason!,
                            ),
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
                        child: Text(_action(context, status)),
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
            title: Text(_action(context, status)),
            content: TextField(
              controller: note,
              decoration: InputDecoration(
                labelText: context.l10n.tr(
                  fa: 'یادداشت — اختیاری',
                  en: 'Note — optional',
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: Text(context.l10n.tr(fa: 'تأیید', en: 'Confirm')),
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
          Text(
            context.l10n.tr(fa: 'تاریخچه وضعیت', en: 'Status history'),
            style: Theme.of(context).textTheme.titleMedium,
          ),
          if (logs.isEmpty)
            Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                context.l10n.tr(
                  fa: 'تغییری ثبت نشده است.',
                  en: 'No changes have been recorded.',
                ),
              ),
            )
          else
            ...logs.map(
              (log) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.circle, size: 12),
                title: Text(
                  '${log.oldStatus == null ? context.l10n.tr(fa: 'شروع', en: 'Started') : serviceRequestStatusLabel(context, log.oldStatus!)} ← ${serviceRequestStatusLabel(context, log.newStatus)}',
                ),
                subtitle: Text(
                  [
                    formatApiDate(context, log.createdAt, showTime: true),
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

String _action(BuildContext context, String status) => switch (status) {
  'accepted' => context.l10n.tr(fa: 'پذیرش درخواست', en: 'Accept request'),
  'rejected' => context.l10n.tr(fa: 'رد درخواست', en: 'Reject request'),
  'in_progress' => context.l10n.tr(fa: 'شروع انجام خدمت', en: 'Start service'),
  'completed' => context.l10n.tr(fa: 'تکمیل خدمت', en: 'Complete service'),
  _ => status,
};
