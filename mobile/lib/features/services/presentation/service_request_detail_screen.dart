import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_request_controller.dart';
import '../../reviews/data/review_models.dart';
import 'service_ui.dart';

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
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'جزئیات درخواست خدمت',
          en: 'Service request details',
        ),
        fallbackLocation: '/services/requests',
      ),
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
                  Padding(
                    padding: EdgeInsets.only(top: 80),
                    child: Center(
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
                                  request.title,
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                              ),
                              Chip(
                                label: Text(
                                  serviceRequestStatusLabel(
                                    context,
                                    request.status,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          if (request.description != null) ...[
                            const SizedBox(height: 8),
                            Text(request.description!),
                          ],
                          const Divider(height: 28),
                          _Info(
                            context.l10n.tr(fa: 'خدمت', en: 'Service'),
                            request.offerTitle ?? '-',
                          ),
                          _Info(
                            context.l10n.tr(fa: 'خدمات‌دهنده', en: 'Provider'),
                            request.providerDisplayName ?? '-',
                          ),
                          _Info(
                            context.l10n.tr(
                              fa: 'روش ارتباط',
                              en: 'Contact method',
                            ),
                            serviceContactMethodLabel(
                              context,
                              request.contactMethod,
                            ),
                          ),
                          _Info(
                            context.l10n.tr(fa: 'تاریخ ثبت', en: 'Created at'),
                            formatApiDate(
                              context,
                              request.createdAt,
                              showTime: true,
                            ),
                          ),
                          if (request.scheduledAt != null)
                            _Info(
                              context.l10n.tr(
                                fa: 'زمان پیشنهادی',
                                en: 'Preferred date',
                              ),
                              formatApiDate(
                                context,
                                request.scheduledAt,
                                showTime: true,
                              ),
                            ),
                          if (request.budgetAmount != null)
                            _Info(
                              context.l10n.tr(fa: 'بودجه', en: 'Budget'),
                              request.currency == 'TOMAN'
                                  ? formatToman(context, request.budgetAmount!)
                                  : '${request.budgetAmount!.toStringAsFixed(0)} ${request.currency}',
                            ),
                          if ((request.addressText ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(fa: 'نشانی', en: 'Address'),
                              request.addressText!,
                            ),
                          if ((request.providerNote ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(
                                fa: 'یادداشت خدمات‌دهنده',
                                en: 'Provider note',
                              ),
                              request.providerNote!,
                            ),
                          if ((request.cancelReason ?? '').isNotEmpty)
                            _Info(
                              context.l10n.tr(
                                fa: 'دلیل لغو',
                                en: 'Cancellation reason',
                              ),
                              request.cancelReason!,
                            ),
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
                            context.l10n.tr(
                              fa: 'تاریخچه وضعیت',
                              en: 'Status history',
                            ),
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 10),
                          if (request.statusLogs.isEmpty)
                            Text(
                              context.l10n.tr(
                                fa: 'تغییر وضعیتی ثبت نشده است.',
                                en: 'No status changes have been recorded.',
                              ),
                            )
                          else
                            ...request.statusLogs.map(
                              (log) => ListTile(
                                contentPadding: EdgeInsets.zero,
                                leading: const Icon(Icons.circle, size: 12),
                                title: Text(
                                  serviceRequestStatusLabel(
                                    context,
                                    log.newStatus,
                                  ),
                                ),
                                subtitle: Text(
                                  [
                                    if (log.oldStatus != null)
                                      context.l10n.tr(
                                        fa:
                                            'از ${serviceRequestStatusLabel(context, log.oldStatus!)}',
                                        en:
                                            'From ${serviceRequestStatusLabel(context, log.oldStatus!)}',
                                      ),
                                    formatApiDate(
                                      context,
                                      log.createdAt,
                                      showTime: true,
                                    ),
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
                      label: Text(
                        context.l10n.tr(
                          fa: 'لغو درخواست',
                          en: 'Cancel request',
                        ),
                      ),
                    ),
                  ],
                  if (request.status == 'completed' &&
                      request.offerId != null) ...[
                    SizedBox(height: r.v(16)),
                    FilledButton.icon(
                      onPressed:
                          () => context.push(
                            '/reviews/create',
                            extra: ReviewCreateTarget(
                              sourceType: 'service_request',
                              sourceId: request.id,
                              subjectType: 'service_offer',
                              subjectId: request.offerId!,
                              title:
                                  request.offerTitle ??
                                  context.l10n.tr(
                                    fa: 'خدمت دریافت‌شده',
                                    en: 'Received service',
                                  ),
                            ),
                          ),
                      icon: const Icon(Icons.rate_review_outlined),
                      label: Text(
                        context.l10n.tr(
                          fa: 'ثبت نظر برای این خدمت',
                          en: 'Review this service',
                        ),
                      ),
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
            title: Text(
              context.l10n.tr(fa: 'لغو درخواست', en: 'Cancel request'),
            ),
            content: TextField(
              controller: reason,
              decoration: InputDecoration(
                labelText: context.l10n.tr(
                  fa: 'دلیل لغو — اختیاری',
                  en: 'Reason — optional',
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Back')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(
                  context.l10n.tr(fa: 'تأیید لغو', en: 'Confirm cancellation'),
                ),
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
