import 'package:flutter/material.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_button.dart';
import '../data/service_models.dart';

class ServiceFinalPriceCard extends StatelessWidget {
  const ServiceFinalPriceCard({
    required this.finalPrice,
    required this.providerView,
    required this.isSaving,
    this.onPropose,
    this.onAccept,
    this.onReject,
    this.onPay,
    super.key,
  });

  final ServiceFinalPrice? finalPrice;
  final bool providerView;
  final bool isSaving;
  final VoidCallback? onPropose;
  final VoidCallback? onAccept;
  final VoidCallback? onReject;
  final VoidCallback? onPay;

  @override
  Widget build(BuildContext context) {
    final price = finalPrice;
    final colors = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(Icons.request_quote_outlined, color: colors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    context.l10n.tr(
                      fa: 'قیمت نهایی و پرداخت',
                      en: 'Final price and payment',
                    ),
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                if (price != null)
                  Chip(label: Text(_status(context, price.status))),
              ],
            ),
            const SizedBox(height: 12),
            if (price == null) ...[
              Text(
                providerView
                    ? context.l10n.tr(
                      fa: 'برای شروع کار، مبلغ قطعی و شرح آن را ارسال کنید.',
                      en:
                          'Send the agreed amount and its description before work starts.',
                    )
                    : context.l10n.tr(
                      fa: 'هنوز قیمت نهایی از طرف خدمات‌دهنده ارسال نشده است.',
                      en: 'The provider has not proposed a final price yet.',
                    ),
              ),
              if (providerView && onPropose != null) ...[
                const SizedBox(height: 12),
                FarmButton(
                  label: context.l10n.tr(
                    fa: 'ارسال قیمت نهایی',
                    en: 'Propose final price',
                  ),
                  icon: Icons.add_card_outlined,
                  expand: true,
                  isLoading: isSaving,
                  onPressed: onPropose,
                ),
              ],
            ] else ...[
              _Info(
                label: context.l10n.tr(fa: 'مبلغ', en: 'Amount'),
                value:
                    price.currency == 'TOMAN'
                        ? formatToman(context, price.amount)
                        : '${price.amount.toStringAsFixed(0)} ${price.currency}',
              ),
              _Info(
                label: context.l10n.tr(fa: 'شرح', en: 'Description'),
                value: price.description,
              ),
              _Info(
                label: context.l10n.tr(fa: 'زمان پیشنهاد', en: 'Proposed at'),
                value: formatApiDate(context, price.proposedAt, showTime: true),
              ),
              if (price.invoiceId != null)
                _Info(
                  label: context.l10n.tr(fa: 'فاکتور', en: 'Invoice'),
                  value: context.l10n.tr(
                    fa:
                        '#${price.invoiceId} • ${_invoiceStatus(context, price.invoiceStatus)}',
                    en:
                        '#${price.invoiceId} • ${_invoiceStatus(context, price.invoiceStatus)}',
                  ),
                ),
              if (price.refundStatus != null)
                _Info(
                  label: context.l10n.tr(fa: 'بازپرداخت', en: 'Refund'),
                  value: _refundStatus(context, price.refundStatus),
                ),
              if (price.isProposed &&
                  !providerView &&
                  (onAccept != null || onReject != null)) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: FarmButton(
                        label: context.l10n.tr(fa: 'رد پیشنهاد', en: 'Reject'),
                        variant: FarmButtonVariant.outline,
                        onPressed: isSaving ? null : onReject,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: FarmButton(
                        label: context.l10n.tr(fa: 'پذیرش قیمت', en: 'Accept'),
                        icon: Icons.check_circle_outline,
                        isLoading: isSaving,
                        onPressed: onAccept,
                      ),
                    ),
                  ],
                ),
              ],
              if (price.isProposed && providerView && onPropose != null) ...[
                const SizedBox(height: 12),
                FarmButton(
                  label: context.l10n.tr(
                    fa: 'ویرایش پیشنهاد',
                    en: 'Revise proposal',
                  ),
                  variant: FarmButtonVariant.secondary,
                  icon: Icons.edit_outlined,
                  expand: true,
                  isLoading: isSaving,
                  onPressed: onPropose,
                ),
              ],
              if (price.isRejected && providerView && onPropose != null) ...[
                const SizedBox(height: 12),
                FarmButton(
                  label: context.l10n.tr(
                    fa: 'ارسال پیشنهاد جدید',
                    en: 'Send a new proposal',
                  ),
                  icon: Icons.refresh,
                  expand: true,
                  isLoading: isSaving,
                  onPressed: onPropose,
                ),
              ],
              if (price.canPay && !providerView && onPay != null) ...[
                const SizedBox(height: 12),
                FarmButton(
                  label: context.l10n.tr(
                    fa: 'پرداخت امن فاکتور',
                    en: 'Pay invoice securely',
                  ),
                  icon: Icons.payments_outlined,
                  expand: true,
                  isLoading: isSaving,
                  onPressed: onPay,
                ),
              ],
              if (price.isAccepted &&
                  !price.isPaid &&
                  !price.hasActiveRefund &&
                  !price.isRefunded &&
                  providerView) ...[
                const SizedBox(height: 8),
                Text(
                  context.l10n.tr(
                    fa: 'پس از تأیید پرداخت مشتری، دکمه شروع خدمت فعال می‌شود.',
                    en:
                        'The start button will be enabled after payment is verified.',
                  ),
                  style: TextStyle(color: colors.tertiary),
                ),
              ],
              if (price.isPaid) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.verified_outlined, color: colors.primary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        context.l10n.tr(
                          fa: 'پرداخت تأیید شده است.',
                          en: 'Payment has been verified.',
                        ),
                      ),
                    ),
                  ],
                ),
              ],
              if (price.hasActiveRefund) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.currency_exchange_rounded,
                      color: colors.tertiary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        price.refundStatus == 'requested'
                            ? context.l10n.tr(
                              fa: 'درخواست بازپرداخت در انتظار بررسی ادمین است.',
                              en: 'The refund request awaits admin review.',
                            )
                            : context.l10n.tr(
                              fa:
                                  'بازپرداخت تأیید شده و در انتظار پردازش مالی است.',
                              en:
                                  'The refund is approved and awaits payment processing.',
                            ),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  String _status(BuildContext context, String value) => switch (value) {
    'proposed' => context.l10n.tr(fa: 'منتظر تصمیم', en: 'Awaiting decision'),
    'accepted' => context.l10n.tr(fa: 'پذیرفته‌شده', en: 'Accepted'),
    'rejected' => context.l10n.tr(fa: 'ردشده', en: 'Rejected'),
    _ => value,
  };

  String _invoiceStatus(BuildContext context, String? value) => switch (value) {
    'payment_pending' => context.l10n.tr(
      fa: 'در انتظار پرداخت',
      en: 'Payment pending',
    ),
    'paid' => context.l10n.tr(fa: 'پرداخت‌شده', en: 'Paid'),
    'cancelled' => context.l10n.tr(fa: 'لغوشده', en: 'Cancelled'),
    'refund_pending' => context.l10n.tr(
      fa: 'بازپرداخت در انتظار',
      en: 'Refund pending',
    ),
    'refunded' => context.l10n.tr(fa: 'بازپرداخت‌شده', en: 'Refunded'),
    _ => value ?? '-',
  };

  String _refundStatus(BuildContext context, String? value) => switch (value) {
    'requested' => context.l10n.tr(
      fa: 'در انتظار بررسی ادمین',
      en: 'Awaiting admin review',
    ),
    'approved' => context.l10n.tr(
      fa: 'تأییدشده، در انتظار پردازش',
      en: 'Approved, awaiting processing',
    ),
    'succeeded' => context.l10n.tr(
      fa: 'با موفقیت بازپرداخت شد',
      en: 'Refunded successfully',
    ),
    'rejected' => context.l10n.tr(fa: 'ردشده', en: 'Rejected'),
    _ => value ?? '-',
  };
}

class _Info extends StatelessWidget {
  const _Info({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 5),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 110, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}
