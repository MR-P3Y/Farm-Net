import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../state/finance_controller.dart';

class FinanceCenterScreen extends ConsumerStatefulWidget {
  const FinanceCenterScreen({super.key});
  @override
  ConsumerState<FinanceCenterScreen> createState() => _FinanceCenterState();
}

class _FinanceCenterState extends ConsumerState<FinanceCenterScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(financeControllerProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(financeControllerProvider);
    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'مرکز مالی من', en: 'My finance center'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(financeControllerProvider.notifier).load(),
        child:
            state.loading && state.wallet == null
                ? const Center(child: CircularProgressIndicator())
                : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    if (state.error != null)
                      Card(
                        color: Theme.of(context).colorScheme.errorContainer,
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Text(state.error!),
                        ),
                      ),
                    _wallet(context, state),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          context.l10n.tr(
                            fa: 'درخواست‌های تسویه',
                            en: 'Settlement requests',
                          ),
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        FilledButton.icon(
                          onPressed:
                              state.wallet == null || state.saving
                                  ? null
                                  : () => _settlementDialog(context),
                          icon: const Icon(Icons.add),
                          label: Text(
                            context.l10n.tr(fa: 'درخواست', en: 'Request'),
                          ),
                        ),
                      ],
                    ),
                    if (state.settlements.isEmpty)
                      Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          context.l10n.tr(
                            fa: 'درخواست تسویه‌ای ثبت نشده است.',
                            en: 'No settlement request has been submitted.',
                          ),
                        ),
                      )
                    else
                      ...state.settlements.map(
                        (row) => Card(
                          child: ListTile(
                            leading: const Icon(Icons.account_balance_outlined),
                            title: Text(formatToman(context, row.amount)),
                            subtitle: Text(
                              '${context.l10n.tr(fa: 'وضعیت', en: 'Status')}: '
                              '${_statusLabel(context, row.status)} • '
                              '${formatDate(context, row.requestedAt.toLocal())}',
                            ),
                          ),
                        ),
                      ),
                    const SizedBox(height: 16),
                    Text(
                      context.l10n.tr(fa: 'فاکتورهای من', en: 'My invoices'),
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    if (state.invoices.isEmpty)
                      Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          context.l10n.tr(
                            fa: 'فاکتوری موجود نیست.',
                            en: 'No invoice is available.',
                          ),
                        ),
                      )
                    else
                      ...state.invoices.map(
                        (row) => Card(
                          child: ListTile(
                            leading: const Icon(Icons.receipt_long_outlined),
                            title: Text(row.number),
                            subtitle: Text(
                              '${_sourceLabel(context, row.sourceType)} • '
                              '${_statusLabel(context, row.status)} • '
                              '${formatDate(context, row.issuedAt.toLocal())}',
                            ),
                            trailing: Text(formatToman(context, row.total)),
                          ),
                        ),
                      ),
                  ],
                ),
      ),
    );
  }

  Widget _wallet(BuildContext context, FinanceState state) {
    final wallet = state.wallet;
    if (wallet == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            this.context.l10n.tr(
              fa: 'کیف پول برای این نقش در دسترس نیست.',
              en: 'A wallet is not available for this role.',
            ),
          ),
        ),
      );
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              context.l10n.tr(fa: 'کیف پول ارائه‌دهنده', en: 'Provider wallet'),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            _amount(
              context,
              context.l10n.tr(fa: 'قابل تسویه', en: 'Available'),
              wallet.available,
            ),
            _amount(
              context,
              context.l10n.tr(fa: 'در انتظار آزادسازی', en: 'Pending release'),
              wallet.pending,
            ),
            _amount(
              context,
              context.l10n.tr(
                fa: 'رزروشده برای تسویه',
                en: 'Reserved for settlement',
              ),
              wallet.reserved,
            ),
            const SizedBox(height: 8),
            Text(
              context.l10n.tr(
                fa: 'تمام مبالغ به تومان ایران هستند.',
                en: 'All amounts are in Iranian Toman.',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _amount(BuildContext context, String label, double value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [Text(label), Text(formatToman(context, value))],
    ),
  );

  Future<void> _settlementDialog(BuildContext context) async {
    final amount = TextEditingController();
    final note = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              context.l10n.tr(fa: 'درخواست تسویه', en: 'Settlement request'),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: amount,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'مبلغ به تومان',
                      en: 'Amount in Toman',
                    ),
                  ),
                ),
                TextField(
                  controller: note,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'یادداشت اختیاری',
                      en: 'Optional note',
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
                child: Text(context.l10n.tr(fa: 'ثبت', en: 'Submit')),
              ),
            ],
          ),
    );
    if (accepted != true || !mounted) {
      return;
    }
    final value = double.tryParse(
      toEnglishDigits(amount.text).replaceAll(',', '').replaceAll('٬', ''),
    );
    if (value == null || value <= 0 || value != value.roundToDouble()) {
      ScaffoldMessenger.of(this.context).showSnackBar(
        SnackBar(
          content: Text(
            this.context.l10n.tr(
              fa: 'مبلغ صحیح و به تومان کامل وارد کنید.',
              en: 'Enter a valid whole amount in Toman.',
            ),
          ),
        ),
      );
      return;
    }
    final ok = await ref
        .read(financeControllerProvider.notifier)
        .requestSettlement(value, note.text);
    if (ok && mounted) {
      ScaffoldMessenger.of(this.context).showSnackBar(
        SnackBar(
          content: Text(
            this.context.l10n.tr(
              fa: 'درخواست تسویه ثبت شد.',
              en: 'Settlement request submitted.',
            ),
          ),
        ),
      );
    }
  }

  String _statusLabel(BuildContext context, String status) {
    final labels = <String, ({String fa, String en})>{
      'payment_pending': (fa: 'در انتظار پرداخت', en: 'Payment pending'),
      'paid': (fa: 'پرداخت‌شده', en: 'Paid'),
      'cancelled': (fa: 'لغوشده', en: 'Cancelled'),
      'requested': (fa: 'ثبت‌شده', en: 'Requested'),
      'approved': (fa: 'تأییدشده', en: 'Approved'),
      'processing': (fa: 'در حال پردازش', en: 'Processing'),
      'completed': (fa: 'تکمیل‌شده', en: 'Completed'),
      'rejected': (fa: 'ردشده', en: 'Rejected'),
      'failed': (fa: 'ناموفق', en: 'Failed'),
    };
    final label = labels[status];
    return label == null ? status : context.l10n.tr(fa: label.fa, en: label.en);
  }

  String _sourceLabel(BuildContext context, String sourceType) {
    final labels = <String, ({String fa, String en})>{
      'service_request': (fa: 'درخواست خدمت', en: 'Service request'),
      'consultation_request': (
        fa: 'درخواست مشاوره',
        en: 'Consultation request',
      ),
      'order': (fa: 'سفارش', en: 'Order'),
      'rental_request': (fa: 'درخواست اجاره', en: 'Rental request'),
    };
    final label = labels[sourceType];
    return label == null
        ? sourceType
        : context.l10n.tr(fa: label.fa, en: label.en);
  }
}
