import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/money.dart';
import '../data/order_models.dart';
import '../state/seller_order_controller.dart';

class SellerOrderDetailScreen extends ConsumerStatefulWidget {
  const SellerOrderDetailScreen({required this.orderId, super.key});

  final int orderId;

  @override
  ConsumerState<SellerOrderDetailScreen> createState() => _State();
}

class _State extends ConsumerState<SellerOrderDetailScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref
          .read(sellerOrderControllerProvider.notifier)
          .loadDetail(widget.orderId),
    );
  }

  Future<void> _advance(Order order) async {
    final noteController = TextEditingController(text: order.sellerNote);
    final note = await showDialog<String?>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              'تغییر وضعیت به ${orderStatusLabelFa(order.sellerNextStatus!)}',
            ),
            content: TextField(
              controller: noteController,
              maxLength: 2000,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'یادداشت فروشنده (اختیاری)',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, noteController.text),
                child: const Text('تأیید تغییر'),
              ),
            ],
          ),
    );
    noteController.dispose();
    if (note == null || !mounted) return;
    final ok = await ref
        .read(sellerOrderControllerProvider.notifier)
        .advance(orderId: order.id, sellerNote: note);
    if (!ok || !mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('وضعیت سفارش با موفقیت به‌روزرسانی شد.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sellerOrderControllerProvider);
    final order = state.selected;
    return Scaffold(
      appBar: AppBar(title: Text(order?.orderNumber ?? 'جزئیات سفارش فروش')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading && order == null) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.isDenied) {
            return const Center(
              child: Text('دسترسی به این سفارش فروش مجاز نیست.'),
            );
          }
          if (state.errorMessage != null && order == null) {
            return Center(child: Text(state.errorMessage!));
          }
          if (order == null) {
            return const Center(child: Text('سفارش فروش پیدا نشد.'));
          }
          return RefreshIndicator(
            onRefresh:
                () => ref
                    .read(sellerOrderControllerProvider.notifier)
                    .loadDetail(widget.orderId),
            child: ListView(
              padding: r.pagePadding(),
              children: [
                _Section(
                  title: 'خلاصه فروش',
                  children: [
                    _Info('وضعیت', orderStatusLabelFa(order.status)),
                    _Info('پرداخت', orderStatusLabelFa(order.paymentStatus)),
                    _Info('مبلغ کل', formatToman(context, order.totalAmount)),
                    _Info('سهم فروشنده', formatToman(context, order.sellerAmount)),
                  ],
                ),
                const SizedBox(height: 12),
                _Section(
                  title: 'اطلاعات تحویل',
                  children: [
                    _Info('شناسه خریدار', order.buyerUserId.toString()),
                    if (order.shippingPhone != null)
                      _Info('شماره تماس', order.shippingPhone!),
                    if (order.shippingAddress != null)
                      _Info('آدرس', order.shippingAddress!),
                    if (order.shippingPostalCode != null)
                      _Info('کد پستی', order.shippingPostalCode!),
                    if (order.buyerNote != null)
                      _Info('یادداشت خریدار', order.buyerNote!),
                  ],
                ),
                const SizedBox(height: 12),
                _Section(
                  title: 'اقلام سفارش',
                  children:
                      order.items.isEmpty
                          ? [const Text('قلمی ثبت نشده است.')]
                          : order.items
                              .map(
                                (item) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  title: Text(item.productNameSnapshot),
                                  subtitle: Text(
                                    '${item.quantity} ${item.unitSnapshot}',
                                  ),
                                  trailing: Text(formatToman(context, item.lineTotal)),
                                ),
                              )
                              .toList(),
                ),
                const SizedBox(height: 12),
                _Section(
                  title: 'تاریخچه وضعیت',
                  children:
                      order.statusHistory.isEmpty
                          ? [const Text('تاریخچه‌ای ثبت نشده است.')]
                          : order.statusHistory
                              .map(
                                (row) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  title: Text(
                                    '${orderStatusLabelFa(row.fromStatus ?? '-')} '
                                    '← ${orderStatusLabelFa(row.toStatus)}',
                                  ),
                                  subtitle:
                                      row.note == null ? null : Text(row.note!),
                                ),
                              )
                              .toList(),
                ),
                if (state.errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                if (order.sellerNextStatus != null) ...[
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: state.isSaving ? null : () => _advance(order),
                    icon: const Icon(Icons.arrow_forward_outlined),
                    label: Text(
                      'تغییر به ${orderStatusLabelFa(order.sellerNextStatus!)}',
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
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          ...children,
        ],
      ),
    ),
  );
}

class _Info extends StatelessWidget {
  const _Info(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 120, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}
