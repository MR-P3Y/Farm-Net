import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/order_models.dart';
import '../state/order_controller.dart';

class OrderDetailScreen extends ConsumerStatefulWidget {
  const OrderDetailScreen({required this.orderId, super.key});

  final int orderId;

  @override
  ConsumerState<OrderDetailScreen> createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends ConsumerState<OrderDetailScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref
          .read(orderControllerProvider.notifier)
          .loadOrderDetail(widget.orderId);
    });
  }

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  Future<void> _pay(Order order) async {
    final ok = await ref.read(orderControllerProvider.notifier).payOrder(order);

    if (!ok || !mounted) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('پرداخت با موفقیت تأیید شد.')));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(orderControllerProvider);
    final order = state.selectedOrder;

    return Scaffold(
      appBar: AppBar(
        title: Text(order == null ? 'جزئیات سفارش' : order.orderNumber),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return const FarmLoadingView();
          }

          if (state.errorMessage != null) {
            return Center(child: Text(state.errorMessage!));
          }

          if (order == null) {
            return const Center(child: Text('سفارش پیدا نشد.'));
          }

          final canPay =
              order.paymentStatus == 'pending' && order.invoiceId != null;

          return RefreshIndicator(
            onRefresh: () {
              return ref
                  .read(orderControllerProvider.notifier)
                  .loadOrderDetail(widget.orderId);
            },
            child: ListView(
              padding: r.pagePadding(),
              children: [
                _SectionCard(
                  title: 'خلاصه سفارش',
                  children: [
                    _InfoRow(label: 'شماره سفارش', value: order.orderNumber),
                    _InfoRow(label: 'وضعیت سفارش', value: order.status),
                    _InfoRow(label: 'وضعیت پرداخت', value: order.paymentStatus),
                    _InfoRow(
                      label: 'مبلغ کل',
                      value: _price(order.totalAmount),
                    ),
                    if (order.shippingAddress != null)
                      _InfoRow(label: 'آدرس', value: order.shippingAddress!),
                    if (order.shippingPhone != null)
                      _InfoRow(label: 'تماس', value: order.shippingPhone!),
                  ],
                ),
                SizedBox(height: r.v(12)),
                if (canPay) ...[
                  FilledButton.icon(
                    onPressed: state.isSaving ? null : () => _pay(order),
                    icon: const Icon(Icons.payments_outlined),
                    label: const Text('پرداخت سفارش'),
                  ),
                  SizedBox(height: r.v(12)),
                ],
                _SectionCard(
                  title: 'آیتم‌ها',
                  children:
                      order.items.isEmpty
                          ? [const Text('آیتمی ثبت نشده است.')]
                          : order.items
                              .map(
                                (item) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(
                                    Icons.inventory_2_outlined,
                                  ),
                                  title: Text(item.productNameSnapshot),
                                  subtitle: Text('تعداد: ${item.quantity}'),
                                  trailing: Text(_price(item.lineTotal)),
                                ),
                              )
                              .toList(),
                ),
                SizedBox(height: r.v(12)),
                _SectionCard(
                  title: 'پرداخت‌ها',
                  children:
                      order.payments.isEmpty
                          ? [const Text('پرداختی ثبت نشده است.')]
                          : order.payments
                              .map(
                                (payment) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(Icons.payment_outlined),
                                  title: Text(payment.status),
                                  subtitle: Text(payment.method),
                                  trailing: Text(_price(payment.amount)),
                                ),
                              )
                              .toList(),
                ),
                SizedBox(height: r.v(12)),
                _SectionCard(
                  title: 'تاریخچه وضعیت',
                  children:
                      order.statusHistory.isEmpty
                          ? [const Text('تاریخچه‌ای ثبت نشده است.')]
                          : order.statusHistory
                              .map(
                                (row) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(Icons.history),
                                  title: Text(
                                    '${row.fromStatus ?? '-'} → ${row.toStatus}',
                                  ),
                                  subtitle: Text(row.note ?? '-'),
                                ),
                              )
                              .toList(),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
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
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
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
}
