import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/app_config.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_request_controller.dart';
import '../state/service_request_state.dart';
import '../../reviews/data/review_models.dart';
import 'service_final_price_card.dart';
import 'service_floating_action_bar.dart';
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
      bottomNavigationBar:
          request == null ? null : _bottomActions(context, state, request),
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
                          if (request.status == 'completed')
                            _Info(
                              context.l10n.tr(
                                fa: 'تأیید اتمام',
                                en: 'Completion confirmation',
                              ),
                              request.completionConfirmedAt == null
                                  ? context.l10n.tr(
                                    fa: 'در انتظار تأیید شما',
                                    en: 'Awaiting your confirmation',
                                  )
                                  : context.l10n.tr(
                                    fa: 'تأیید شده و وجه آزاد شده',
                                    en: 'Confirmed and funds released',
                                  ),
                            ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                  if ({
                    'accepted',
                    'in_progress',
                    'completed',
                  }.contains(request.status)) ...[
                    ServiceFinalPriceCard(
                      finalPrice: state.finalPrice,
                      providerView: false,
                      isSaving: state.isSaving,
                    ),
                    SizedBox(height: r.v(12)),
                  ],
                  if ({
                    'open',
                    'accepted',
                    'in_progress',
                  }.contains(request.status)) ...[
                    _CancellationPolicyCard(
                      directCancellationAvailable:
                          request.canCancel && state.finalPrice?.isPaid != true,
                    ),
                    SizedBox(height: r.v(12)),
                  ],
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
                                    if ((log.note ?? '').isNotEmpty)
                                      serviceStatusNoteLabel(
                                        context,
                                        log.note!,
                                      ),
                                  ].join(' • '),
                                ),
                              ),
                            ),
                        ],
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

  Widget? _bottomActions(
    BuildContext context,
    ServiceRequestState state,
    ServiceRequest request,
  ) {
    final price = state.finalPrice;
    final saving = state.isSaving;
    final canDirectCancel = request.canCancel && price?.isPaid != true;
    ServiceAction? cancelAction;
    if (canDirectCancel) {
      cancelAction = ServiceAction(
        label: context.l10n.tr(fa: 'لغو درخواست', en: 'Cancel request'),
        icon: Icons.cancel_outlined,
        variant: FarmButtonVariant.destructive,
        onPressed: saving ? null : () => _cancel(request),
      );
    }
    final canRequestRefund =
        price?.canRequestRefund == true &&
        {'accepted', 'in_progress', 'completed'}.contains(request.status);
    final refundAction =
        canRequestRefund
            ? ServiceAction(
              label: context.l10n.tr(
                fa: 'لغو و بازپرداخت',
                en: 'Cancel and refund',
              ),
              icon: Icons.currency_exchange_rounded,
              variant: FarmButtonVariant.destructive,
              onPressed: saving ? null : () => _requestRefund(request),
            )
            : null;

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
          icon: Icons.hourglass_top_rounded,
          onPressed: null,
        ),
      );
    }

    if (price?.isProposed == true) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(fa: 'پذیرش قیمت', en: 'Accept price'),
          icon: Icons.check_circle_outline,
          isLoading: saving,
          onPressed: saving ? null : () => _decide(request.id, 'accept'),
        ),
        secondary: ServiceAction(
          label: context.l10n.tr(fa: 'رد پیشنهاد', en: 'Reject proposal'),
          icon: Icons.close_rounded,
          variant: FarmButtonVariant.outline,
          onPressed: saving ? null : () => _decide(request.id, 'reject'),
        ),
        tertiary: cancelAction,
      );
    }

    if (price?.canPay == true) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'پرداخت امن فاکتور',
            en: 'Pay invoice securely',
          ),
          icon: Icons.payments_outlined,
          isLoading: saving,
          onPressed:
              saving
                  ? null
                  : () =>
                      _pay(requestId: request.id, invoiceId: price!.invoiceId!),
        ),
        tertiary: cancelAction,
      );
    }

    if (request.status == 'completed' &&
        request.completionConfirmedAt == null) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'تأیید انجام خدمت و آزادسازی وجه',
            en: 'Confirm service and release funds',
          ),
          icon: Icons.verified_user_outlined,
          isLoading: saving,
          onPressed: saving ? null : () => _confirmCompletion(request),
        ),
        tertiary: refundAction,
      );
    }

    if (request.status == 'completed' && request.offerId != null) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'ثبت نظر برای این خدمت',
            en: 'Review this service',
          ),
          icon: Icons.rate_review_outlined,
          onPressed: () => _review(request),
        ),
        tertiary: refundAction,
      );
    }

    if (request.status == 'accepted' && price?.isPaid == true) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'پرداخت شد؛ منتظر شروع خدمت',
            en: 'Paid; waiting for service to start',
          ),
          icon: Icons.verified_outlined,
          onPressed: null,
        ),
        tertiary: refundAction,
      );
    }

    if (request.status == 'in_progress' && price?.isPaid == true) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label: context.l10n.tr(
            fa: 'خدمت در حال انجام است',
            en: 'Service is in progress',
          ),
          icon: Icons.engineering_outlined,
          onPressed: null,
        ),
        tertiary: refundAction,
      );
    }

    if (canDirectCancel) {
      return ServiceFloatingActionBar(
        primary: ServiceAction(
          label:
              request.status == 'open'
                  ? context.l10n.tr(
                    fa: 'در انتظار پذیرش خدمات‌دهنده',
                    en: 'Waiting for provider acceptance',
                  )
                  : context.l10n.tr(
                    fa: 'در انتظار قیمت نهایی',
                    en: 'Waiting for final price',
                  ),
          icon: Icons.hourglass_bottom_rounded,
          onPressed: null,
        ),
        tertiary: cancelAction,
      );
    }
    return null;
  }

  void _review(ServiceRequest request) {
    context.push(
      '/reviews/create',
      extra: ReviewCreateTarget(
        sourceType: 'service_request',
        sourceId: request.id,
        subjectType: 'service_offer',
        subjectId: request.offerId!,
        title:
            request.offerTitle ??
            context.l10n.tr(fa: 'خدمت دریافت‌شده', en: 'Received service'),
      ),
    );
  }

  Future<void> _decide(int requestId, String decision) async {
    final accepting = decision == 'accept';
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              accepting
                  ? context.l10n.tr(
                    fa: 'پذیرش قیمت نهایی',
                    en: 'Accept final price',
                  )
                  : context.l10n.tr(
                    fa: 'رد پیشنهاد قیمت',
                    en: 'Reject price proposal',
                  ),
            ),
            content: Text(
              accepting
                  ? context.l10n.tr(
                    fa: 'با پذیرش قیمت، فاکتور قطعی صادر می‌شود.',
                    en: 'Accepting creates the final invoice.',
                  )
                  : context.l10n.tr(
                    fa: 'خدمات‌دهنده می‌تواند پیشنهاد جدیدی ارسال کند.',
                    en: 'The provider can send a revised proposal.',
                  ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(context.l10n.tr(fa: 'تأیید', en: 'Confirm')),
              ),
            ],
          ),
    );
    if (confirmed != true || !mounted) return;
    await ref
        .read(serviceRequestControllerProvider.notifier)
        .decideFinalPrice(requestId, decision);
  }

  Future<void> _pay({required int requestId, required int invoiceId}) async {
    final host = Uri.tryParse(AppConfig.apiBaseUrl)?.host;
    final provider =
        host == 'localhost' || host == '127.0.0.1' ? 'mock' : 'zarinpal';
    final attempt = await ref
        .read(serviceRequestControllerProvider.notifier)
        .payInvoice(
          requestId: requestId,
          invoiceId: invoiceId,
          provider: provider,
        );
    if (!mounted || attempt == null) return;
    if (attempt.isSucceeded) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'پرداخت با موفقیت تأیید شد.',
              en: 'Payment was verified successfully.',
            ),
          ),
        ),
      );
      return;
    }
    final link = attempt.redirectUrl;
    if (link == null || link.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: link));
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              context.l10n.tr(fa: 'ادامه پرداخت', en: 'Continue payment'),
            ),
            content: Text(
              context.l10n.tr(
                fa:
                    'لینک امن درگاه کپی شد. پس از پرداخت، این صفحه را تازه‌سازی کنید.',
                en:
                    'The secure gateway link was copied. Refresh this page after payment.',
              ),
            ),
            actions: [
              FilledButton(
                onPressed: () => Navigator.pop(context),
                child: Text(context.l10n.tr(fa: 'متوجه شدم', en: 'Got it')),
              ),
            ],
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

  Future<void> _requestRefund(ServiceRequest request) async {
    final reason = TextEditingController();
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (dialogContext) => AlertDialog(
            title: Text(
              context.l10n.tr(
                fa: 'لغو و درخواست بازپرداخت',
                en: 'Cancel and request refund',
              ),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  request.status == 'accepted'
                      ? context.l10n.tr(
                        fa:
                            'چون خدمت هنوز شروع نشده، بازپرداخت کامل تأیید می‌شود و فقط پردازش مالی باقی می‌ماند.',
                        en:
                            'Because work has not started, a full refund is approved and only payment processing remains.',
                      )
                      : context.l10n.tr(
                        fa:
                            'چون خدمت شروع شده است، درخواست بازپرداخت کامل برای بررسی ادمین ارسال می‌شود.',
                        en:
                            'Because work has started, the full-refund request will be sent for admin review.',
                      ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: reason,
                  minLines: 2,
                  maxLines: 4,
                  maxLength: 1000,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'دلیل لغو و بازپرداخت',
                      en: 'Cancellation and refund reason',
                    ),
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Back')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: Text(
                  context.l10n.tr(fa: 'ثبت درخواست', en: 'Submit request'),
                ),
              ),
            ],
          ),
    );
    final value = reason.text.trim();
    if (confirmed == true && value.length >= 3 && mounted) {
      await ref
          .read(serviceRequestControllerProvider.notifier)
          .requestRefund(request.id, reason: value);
    } else if (confirmed == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'دلیل باید حداقل سه حرف باشد.',
              en: 'The reason must contain at least three characters.',
            ),
          ),
        ),
      );
    }
    reason.dispose();
  }

  Future<void> _confirmCompletion(ServiceRequest request) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (dialogContext) => AlertDialog(
            title: Text(
              context.l10n.tr(
                fa: 'تأیید انجام کامل خدمت',
                en: 'Confirm completed service',
              ),
            ),
            content: Text(
              context.l10n.tr(
                fa:
                    'با تأیید شما، سهم خدمات‌دهنده از حالت در انتظار به موجودی قابل‌برداشت منتقل می‌شود.',
                en:
                    'Your confirmation moves the provider share from pending to available balance.',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(context.l10n.tr(fa: 'فعلاً نه', en: 'Not now')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: Text(context.l10n.tr(fa: 'تأیید', en: 'Confirm')),
              ),
            ],
          ),
    );
    if (confirmed == true && mounted) {
      await ref
          .read(serviceRequestControllerProvider.notifier)
          .confirmCompletion(request.id);
    }
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

class _CancellationPolicyCard extends StatelessWidget {
  const _CancellationPolicyCard({required this.directCancellationAvailable});

  final bool directCancellationAvailable;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.secondaryContainer.withValues(alpha: .48),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colors.outlineVariant.withValues(alpha: .7)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              directCancellationAvailable
                  ? Icons.info_outline_rounded
                  : Icons.policy_outlined,
              size: 20,
              color: colors.onSecondaryContainer,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                directCancellationAvailable
                    ? context.l10n.tr(
                      fa:
                          'لغو تا پیش از پرداخت رایگان است؛ پس از پرداخت، فقط از مسیر لغو و بازپرداخت پیگیری می‌شود.',
                      en:
                          'Cancellation is free before payment; after payment, use the cancellation and refund process.',
                    )
                    : context.l10n.tr(
                      fa:
                          'پرداخت انجام شده است؛ لغو مستقیم ممکن نیست و باید از مسیر لغو و بازپرداخت پیگیری شود.',
                      en:
                          'Payment is complete; direct cancellation is unavailable and must follow the cancellation and refund process.',
                    ),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: colors.onSecondaryContainer,
                  height: 1.45,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
