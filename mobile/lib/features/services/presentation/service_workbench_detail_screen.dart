import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_button.dart';
import '../data/service_models.dart';
import '../state/service_workbench_controller.dart';
import 'service_final_price_card.dart';
import 'service_floating_action_bar.dart';
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
      bottomNavigationBar: q == null ? null : _bottomActions(context, s, q),
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
                  if ({
                    'accepted',
                    'in_progress',
                    'completed',
                  }.contains(q.status)) ...[
                    ServiceFinalPriceCard(
                      finalPrice: s.finalPrice,
                      providerView: true,
                      isSaving: s.isSaving,
                    ),
                    const SizedBox(height: 12),
                  ],
                  _Timeline(logs: q.statusLogs),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget? _bottomActions(
    BuildContext context,
    ServiceWorkbenchState state,
    ServiceRequest request,
  ) {
    final saving = state.isSaving;
    final price = state.finalPrice;
    if (price?.hasActiveRefund == true) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label:
              price!.refundStatus == 'requested'
                  ? context.l10n.tr(
                    fa: 'بازپرداخت در انتظار بررسی ادمین',
                    en: 'Refund awaiting admin review',
                  )
                  : context.l10n.tr(
                    fa: 'بازپرداخت تأیید شد؛ در انتظار پردازش',
                    en: 'Refund approved; awaiting processing',
                  ),
          icon: Icons.currency_exchange_rounded,
          onPressed: null,
        ),
      );
    }
    if (request.status == 'open') {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'پذیرش و تعیین قیمت',
            en: 'Accept and set price',
          ),
          icon: Icons.price_check_rounded,
          isLoading: saving,
          onPressed: saving ? null : () => _propose(request, acceptFirst: true),
        ),
        secondary: ServiceAction(
          label: context.l10n.tr(fa: 'رد درخواست', en: 'Reject request'),
          icon: Icons.close_rounded,
          variant: FarmButtonVariant.outline,
          onPressed: saving ? null : () => _confirm(request, 'rejected'),
        ),
      );
    }

    if (request.status == 'accepted') {
      if (price == null || price.isRejected || price.isProposed) {
        return ServiceFloatingActionBar(
          primary: ServiceAction(
            label:
                price == null
                    ? context.l10n.tr(
                      fa: 'تعیین قیمت نهایی',
                      en: 'Set final price',
                    )
                    : price.isRejected
                    ? context.l10n.tr(
                      fa: 'ارسال قیمت جدید',
                      en: 'Send a new price',
                    )
                    : context.l10n.tr(
                      fa: 'ویرایش قیمت پیشنهادی',
                      en: 'Revise proposed price',
                    ),
            icon: Icons.request_quote_outlined,
            isLoading: saving,
            onPressed: saving ? null : () => _propose(request),
          ),
        );
      }
      if (price.isAccepted && price.isPaid) {
        return ServiceFloatingActionBar(
          primary: ServiceAction(
            label: context.l10n.tr(fa: 'شروع انجام خدمت', en: 'Start service'),
            icon: Icons.play_arrow_rounded,
            isLoading: saving,
            onPressed: saving ? null : () => _confirm(request, 'in_progress'),
          ),
        );
      }
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'در انتظار پرداخت مشتری',
            en: 'Waiting for customer payment',
          ),
          icon: Icons.hourglass_bottom_rounded,
          onPressed: null,
        ),
      );
    }

    if (request.status == 'in_progress') {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'تکمیل انجام خدمت',
            en: 'Complete service',
          ),
          icon: Icons.task_alt_rounded,
          isLoading: saving,
          onPressed: saving ? null : () => _confirm(request, 'completed'),
        ),
      );
    }
    if (request.status == 'completed') {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label:
              request.completionConfirmedAt == null
                  ? context.l10n.tr(
                    fa: 'در انتظار تأیید درخواست‌کننده',
                    en: 'Awaiting requester confirmation',
                  )
                  : context.l10n.tr(
                    fa: 'اتمام تأیید شد؛ وجه آزاد است',
                    en: 'Completion confirmed; funds released',
                  ),
          icon:
              request.completionConfirmedAt == null
                  ? Icons.hourglass_top_rounded
                  : Icons.account_balance_wallet_outlined,
          onPressed: null,
        ),
      );
    }
    return null;
  }

  Future<void> _propose(
    ServiceRequest request, {
    bool acceptFirst = false,
  }) async {
    final current = ref.read(serviceWorkbenchProvider).finalPrice;
    final amount = TextEditingController(
      text:
          current == null || current.amount <= 0
              ? ''
              : current.amount.toStringAsFixed(0),
    );
    final description = TextEditingController(
      text: current?.description ?? request.title,
    );
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              context.l10n.tr(
                fa: 'پیشنهاد قیمت نهایی',
                en: 'Propose final price',
              ),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: amount,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'مبلغ قطعی به تومان',
                      en: 'Final amount in Toman',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: description,
                  minLines: 2,
                  maxLines: 4,
                  maxLength: 500,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'شرح مبلغ و محدوده کار',
                      en: 'Amount and work scope description',
                    ),
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(context.l10n.tr(fa: 'ارسال', en: 'Send')),
              ),
            ],
          ),
    );
    if (accepted != true || !mounted) {
      amount.dispose();
      description.dispose();
      return;
    }
    final value = double.tryParse(
      toEnglishDigits(amount.text).replaceAll(',', '').trim(),
    );
    final note = description.text.trim();
    if (value == null ||
        value <= 0 ||
        value != value.roundToDouble() ||
        note.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'مبلغ کامل و شرح حداقل سه‌حرفی وارد کنید.',
              en:
                  'Enter a whole Toman amount and a description of at least three characters.',
            ),
          ),
        ),
      );
      amount.dispose();
      description.dispose();
      return;
    }
    final controller = ref.read(serviceWorkbenchProvider.notifier);
    if (acceptFirst) {
      final didAccept = await controller.update(request.id, 'accepted');
      if (!didAccept || !mounted) {
        amount.dispose();
        description.dispose();
        return;
      }
    }
    await controller.proposeFinalPrice(
      requestId: request.id,
      amount: value,
      description: note,
    );
    amount.dispose();
    description.dispose();
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
                    if ((log.note ?? '').isNotEmpty)
                      serviceStatusNoteLabel(context, log.note!),
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
