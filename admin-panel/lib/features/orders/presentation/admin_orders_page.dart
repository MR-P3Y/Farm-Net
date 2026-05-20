import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_order_models.dart';
import '../state/admin_order_controller.dart';

class AdminOrdersPage extends ConsumerStatefulWidget {
  const AdminOrdersPage({super.key});

  @override
  ConsumerState<AdminOrdersPage> createState() => _AdminOrdersPageState();
}

class _AdminOrdersPageState extends ConsumerState<AdminOrdersPage> {
  bool _loaded = false;
  String? _statusFilter;
  String? _paymentStatusFilter;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminOrderControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() {
    return ref
        .read(adminOrderControllerProvider.notifier)
        .load(status: _statusFilter, paymentStatus: _paymentStatusFilter);
  }

  Future<void> _openDetail(AdminOrder item) async {
    await ref.read(adminOrderControllerProvider.notifier).loadDetail(item.id);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _OrderDetailDialog(orderId: item.id),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminOrderControllerProvider);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return Padding(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    'سفارش‌ها',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Refresh',
                    onPressed: _reload,
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  SizedBox(
                    width: r.isCompact ? double.infinity : 300,
                    child: DropdownButtonFormField<String?>(
                      value: _statusFilter,
                      decoration: const InputDecoration(
                        labelText: 'وضعیت سفارش',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'pending_payment',
                          child: Text('در انتظار پرداخت'),
                        ),
                        DropdownMenuItem(
                          value: 'paid',
                          child: Text('پرداخت شده'),
                        ),
                        DropdownMenuItem(
                          value: 'confirmed',
                          child: Text('تأیید شده'),
                        ),
                        DropdownMenuItem(
                          value: 'processing',
                          child: Text('در حال آماده‌سازی'),
                        ),
                        DropdownMenuItem(
                          value: 'shipped',
                          child: Text('ارسال شده'),
                        ),
                        DropdownMenuItem(
                          value: 'delivered',
                          child: Text('تحویل شده'),
                        ),
                        DropdownMenuItem(
                          value: 'cancelled',
                          child: Text('لغو شده'),
                        ),
                        DropdownMenuItem(
                          value: 'refunded',
                          child: Text('ریفاند شده'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 260,
                    child: DropdownButtonFormField<String?>(
                      value: _paymentStatusFilter,
                      decoration: const InputDecoration(
                        labelText: 'وضعیت پرداخت',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'pending',
                          child: Text('pending'),
                        ),
                        DropdownMenuItem(value: 'paid', child: Text('paid')),
                        DropdownMenuItem(
                          value: 'failed',
                          child: Text('failed'),
                        ),
                        DropdownMenuItem(
                          value: 'refunded',
                          child: Text('refunded'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _paymentStatusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                ],
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 16),
              Expanded(
                child:
                    state.isLoading
                        ? const AdminLoadingView()
                        : _OrderTable(items: state.items, onOpen: _openDetail),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _OrderTable extends StatelessWidget {
  const _OrderTable({required this.items, required this.onOpen});

  final List<AdminOrder> items;
  final ValueChanged<AdminOrder> onOpen;

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'سفارشی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('شماره سفارش')),
          DataColumn(label: Text('وضعیت')),
          DataColumn(label: Text('پرداخت')),
          DataColumn(label: Text('مبلغ')),
          DataColumn(label: Text('عملیات')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.orderNumber)),
                  DataCell(Text(item.status)),
                  DataCell(Text(item.paymentStatus)),
                  DataCell(Text(_price(item.totalAmount))),
                  DataCell(
                    TextButton(
                      onPressed: () => onOpen(item),
                      child: const Text('جزئیات'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }
}

class _OrderDetailDialog extends ConsumerStatefulWidget {
  const _OrderDetailDialog({required this.orderId});

  final int orderId;

  @override
  ConsumerState<_OrderDetailDialog> createState() => _OrderDetailDialogState();
}

class _OrderDetailDialogState extends ConsumerState<_OrderDetailDialog> {
  final _noteController = TextEditingController();

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  Future<void> _updateStatus(String status) async {
    final ok = await ref
        .read(adminOrderControllerProvider.notifier)
        .updateStatus(
          orderId: widget.orderId,
          status: status,
          adminNote: _noteController.text.trim(),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminOrderControllerProvider);
    final order = state.selected;

    if (order == null) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    final canCancel = {
      'pending_payment',
      'paid',
      'confirmed',
      'processing',
    }.contains(order.status);
    final canRefund = order.status == 'delivered';

    return AlertDialog(
      title: Text('سفارش #${order.id}'),
      content: SizedBox(
        width: 860,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.72,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _DetailLine(label: 'شماره سفارش', value: order.orderNumber),
                _DetailLine(
                  label: 'خریدار',
                  value: order.buyerUserId.toString(),
                ),
                _DetailLine(label: 'فروشگاه', value: order.storeId.toString()),
                _DetailLine(label: 'وضعیت', value: order.status),
                _DetailLine(label: 'پرداخت', value: order.paymentStatus),
                _DetailLine(label: 'مبلغ کل', value: _price(order.totalAmount)),
                _DetailLine(
                  label: 'کمیسیون',
                  value:
                      '${order.commissionPercent}% / ${_price(order.commissionAmount)}',
                ),
                _DetailLine(
                  label: 'سهم فروشنده',
                  value: _price(order.sellerAmount),
                ),
                if (order.shippingAddress != null)
                  _DetailLine(label: 'آدرس', value: order.shippingAddress!),
                if (order.shippingPhone != null)
                  _DetailLine(label: 'تماس', value: order.shippingPhone!),
                const Divider(height: 28),
                Text('آیتم‌ها', style: Theme.of(context).textTheme.titleMedium),
                if (order.items.isEmpty)
                  const Text('آیتمی ثبت نشده است.')
                else
                  ...order.items.map(
                    (item) => ListTile(
                      dense: true,
                      leading: const Icon(Icons.inventory_2_outlined),
                      title: Text(item.productNameSnapshot),
                      subtitle: Text(
                        'تعداد: ${item.quantity} / مبلغ: ${_price(item.lineTotal)}',
                      ),
                    ),
                  ),
                const Divider(height: 28),
                Text(
                  'پرداخت‌ها',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                if (order.payments.isEmpty)
                  const Text('پرداختی ثبت نشده است.')
                else
                  ...order.payments.map(
                    (payment) => ListTile(
                      dense: true,
                      leading: const Icon(Icons.payments_outlined),
                      title: Text('${payment.method} / ${payment.status}'),
                      subtitle: Text(_price(payment.amount)),
                    ),
                  ),
                const Divider(height: 28),
                Text('تاریخچه', style: Theme.of(context).textTheme.titleMedium),
                if (order.statusHistory.isEmpty)
                  const Text('تاریخچه‌ای ثبت نشده است.')
                else
                  ...order.statusHistory.map(
                    (row) => ListTile(
                      dense: true,
                      leading: const Icon(Icons.history),
                      title: Text(
                        '${row.fromStatus ?? '-'} -> ${row.toStatus}',
                      ),
                      subtitle: Text(row.note ?? '-'),
                    ),
                  ),
                const Divider(height: 28),
                TextField(
                  controller: _noteController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'یادداشت ادمین',
                    border: OutlineInputBorder(),
                  ),
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
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: state.isSaving ? null : () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
        if (canCancel)
          OutlinedButton.icon(
            onPressed: state.isSaving ? null : () => _updateStatus('cancelled'),
            icon: const Icon(Icons.cancel_outlined),
            label: const Text('لغو سفارش'),
          ),
        if (canRefund)
          FilledButton.icon(
            onPressed: state.isSaving ? null : () => _updateStatus('refunded'),
            icon: const Icon(Icons.assignment_return_outlined),
            label: const Text('Refund'),
          ),
      ],
    );
  }
}

class _DetailLine extends StatelessWidget {
  const _DetailLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
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
