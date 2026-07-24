import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_request_controller.dart';
import '../../reviews/data/review_models.dart';

class ServiceRequestDetailScreen extends ConsumerStatefulWidget {
  const ServiceRequestDetailScreen({required this.requestId, super.key});
  final int requestId;
  @override
  ConsumerState<ServiceRequestDetailScreen> createState() => _State();
}

class _State extends ConsumerState<ServiceRequestDetailScreen> {
  bool _loaded = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref
          .read(serviceRequestControllerProvider.notifier)
          .loadDetail(widget.requestId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceRequestControllerProvider);
    final request =
        state.selected?.id == widget.requestId ? state.selected : null;
    return Scaffold(
      appBar: AppBar(title: const Text('جزئیات درخواست خدمت')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) return const FarmLoadingView();
          return RefreshIndicator(
            onRefresh:
                () => ref
                    .read(serviceRequestControllerProvider.notifier)
                    .loadDetail(widget.requestId),
            child: ListView(
              padding: r.pagePadding(),
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                if (state.isSaving) const LinearProgressIndicator(),
                if (state.errorMessage != null)
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (state.successMessage != null)
                  Text(
                    state.successMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                if (request == null)
                  const Padding(
                    padding: EdgeInsets.only(top: 80),
                    child: Center(child: Text('درخواست پیدا نشد.')),
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
                                  request.title,
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                              ),
                              Chip(label: Text(_statusLabel(request.status))),
                            ],
                          ),
                          if (request.description != null) ...[
                            const SizedBox(height: 8),
                            Text(request.description!),
                          ],
                          const Divider(height: 28),
                          _Info('خدمت', request.offerTitle ?? '-'),
                          _Info(
                            'خدمات‌دهنده',
                            request.providerDisplayName ?? '-',
                          ),
                          _Info(
                            'روش ارتباط',
                            _contactLabel(request.contactMethod),
                          ),
                          if (request.budgetAmount != null)
                            _Info(
                              'بودجه',
                              '${request.budgetAmount!.toStringAsFixed(0)} ${request.currency == 'TOMAN' ? 'تومان' : request.currency}',
                            ),
                          if ((request.addressText ?? '').isNotEmpty)
                            _Info('نشانی', request.addressText!),
                          if ((request.providerNote ?? '').isNotEmpty)
                            _Info('یادداشت خدمات‌دهنده', request.providerNote!),
                          if ((request.cancelReason ?? '').isNotEmpty)
                            _Info('دلیل لغو', request.cancelReason!),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'تاریخچه وضعیت',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 10),
                          if (request.statusLogs.isEmpty)
                            const Text('تغییر وضعیتی ثبت نشده است.')
                          else
                            ...request.statusLogs.map(
                              (log) => ListTile(
                                contentPadding: EdgeInsets.zero,
                                leading: const Icon(Icons.circle, size: 12),
                                title: Text(_statusLabel(log.newStatus)),
                                subtitle: Text(
                                  [
                                    if (log.oldStatus != null)
                                      'از ${_statusLabel(log.oldStatus!)}',
                                    if ((log.note ?? '').isNotEmpty) log.note!,
                                  ].join(' • '),
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                  if (request.canCancel) ...[
                    SizedBox(height: r.v(16)),
                    OutlinedButton.icon(
                      onPressed: state.isSaving ? null : () => _cancel(request),
                      icon: const Icon(Icons.cancel_outlined),
                      label: const Text('لغو درخواست'),
                    ),
                  ],
                  if (request.status == 'completed' &&
                      request.offerId != null) ...[
                    SizedBox(height: r.v(16)),
                    FilledButton.icon(
                      onPressed: () => context.push(
                        '/reviews/create',
                        extra: ReviewCreateTarget(
                          sourceType: 'service_request',
                          sourceId: request.id,
                          subjectType: 'service_offer',
                          subjectId: request.offerId!,
                          title: request.offerTitle ?? 'خدمت دریافت‌شده',
                        ),
                      ),
                      icon: const Icon(Icons.rate_review_outlined),
                      label: const Text('ثبت نظر برای این خدمت'),
                    ),
                  ],
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _cancel(ServiceRequest request) async {
    final reason = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('لغو درخواست'),
            content: TextField(
              controller: reason,
              decoration: const InputDecoration(
                labelText: 'دلیل لغو — اختیاری',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('تأیید لغو'),
              ),
            ],
          ),
    );
    if (confirmed == true) {
      await ref
          .read(serviceRequestControllerProvider.notifier)
          .cancel(request.id, reason: reason.text.trim());
    }
    reason.dispose();
  }
}

class _Info extends StatelessWidget {
  const _Info(this.label, this.value);
  final String label;
  final String value;
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

String _contactLabel(String? method) =>
    const {
      'in_app': 'داخل اپلیکیشن',
      'phone': 'تلفنی',
      'video': 'تصویری',
      'visit': 'حضوری',
    }[method] ??
    '-';

String _statusLabel(String status) =>
    const {
      'open': 'باز',
      'accepted': 'پذیرفته‌شده',
      'in_progress': 'در حال انجام',
      'completed': 'تکمیل‌شده',
      'cancelled': 'لغوشده',
      'rejected': 'ردشده',
    }[status] ??
    status;
