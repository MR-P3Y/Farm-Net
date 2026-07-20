import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
      appBar: const FarmAppBar(title: 'مرکز مالی من'),
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
                          'درخواست‌های تسویه',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        FilledButton.icon(
                          onPressed:
                              state.wallet == null || state.saving
                                  ? null
                                  : () => _settlementDialog(context),
                          icon: const Icon(Icons.add),
                          label: const Text('درخواست'),
                        ),
                      ],
                    ),
                    if (state.settlements.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(20),
                        child: Text('درخواست تسویه‌ای ثبت نشده است.'),
                      )
                    else
                      ...state.settlements.map(
                        (row) => Card(
                          child: ListTile(
                            leading: const Icon(Icons.account_balance_outlined),
                            title: Text(formatToman(row.amount)),
                            subtitle: Text('وضعیت: ${row.status}'),
                          ),
                        ),
                      ),
                    const SizedBox(height: 16),
                    Text(
                      'فاکتورهای من',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    if (state.invoices.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(20),
                        child: Text('فاکتوری موجود نیست.'),
                      )
                    else
                      ...state.invoices.map(
                        (row) => Card(
                          child: ListTile(
                            leading: const Icon(Icons.receipt_long_outlined),
                            title: Text(row.number),
                            subtitle: Text('${row.sourceType} • ${row.status}'),
                            trailing: Text(formatToman(row.total)),
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
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('کیف پول برای این نقش در دسترس نیست.'),
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
              'کیف پول ارائه‌دهنده',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            _amount('قابل تسویه', wallet.available),
            _amount('در انتظار آزادسازی', wallet.pending),
            _amount('رزروشده برای تسویه', wallet.reserved),
            const SizedBox(height: 8),
            const Text('تمام مبالغ به تومان ایران هستند.'),
          ],
        ),
      ),
    );
  }

  Widget _amount(String label, double value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [Text(label), Text(formatToman(value))],
    ),
  );

  Future<void> _settlementDialog(BuildContext context) async {
    final amount = TextEditingController();
    final note = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('درخواست تسویه'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: amount,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'مبلغ به تومان'),
                ),
                TextField(
                  controller: note,
                  decoration: const InputDecoration(
                    labelText: 'یادداشت اختیاری',
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('ثبت'),
              ),
            ],
          ),
    );
    if (accepted != true || !mounted) {
      return;
    }
    final value = double.tryParse(amount.text.replaceAll(',', ''));
    if (value == null || value <= 0 || value != value.roundToDouble()) {
      ScaffoldMessenger.of(this.context).showSnackBar(
        const SnackBar(content: Text('مبلغ صحیح و به تومان کامل وارد کنید.')),
      );
      return;
    }
    final ok = await ref
        .read(financeControllerProvider.notifier)
        .requestSettlement(value, note.text);
    if (ok && mounted) {
      ScaffoldMessenger.of(
        this.context,
      ).showSnackBar(const SnackBar(content: Text('درخواست تسویه ثبت شد.')));
    }
  }
}
