import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../data/order_models.dart';
import '../state/seller_order_controller.dart';

class SellerOrdersScreen extends ConsumerStatefulWidget {
  const SellerOrdersScreen({super.key});

  @override
  ConsumerState<SellerOrdersScreen> createState() => _SellerOrdersScreenState();
}

class _SellerOrdersScreenState extends ConsumerState<SellerOrdersScreen> {
  bool _loaded = false;
  String? _status;

  static const _statuses = [
    'pending_payment',
    'paid',
    'confirmed',
    'processing',
    'shipped',
    'delivered',
    'cancelled',
    'refunded',
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(sellerOrderControllerProvider.notifier).loadList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sellerOrderControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('سفارش‌های فروش من')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading && state.items.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.isDenied) {
            return _SellerDenied(
              onRetry:
                  () => ref
                      .read(sellerOrderControllerProvider.notifier)
                      .loadList(status: _status),
            );
          }
          return RefreshIndicator(
            onRefresh:
                () => ref
                    .read(sellerOrderControllerProvider.notifier)
                    .loadList(page: state.page, status: _status),
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: r.pagePadding(),
              children: [
                DropdownButtonFormField<String?>(
                  initialValue: _status,
                  decoration: const InputDecoration(
                    labelText: 'فیلتر وضعیت سفارش',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('همه')),
                    ..._statuses.map(
                      (status) => DropdownMenuItem(
                        value: status,
                        child: Text(orderStatusLabelFa(status)),
                      ),
                    ),
                  ],
                  onChanged: (value) {
                    setState(() => _status = value);
                    ref
                        .read(sellerOrderControllerProvider.notifier)
                        .loadList(status: value);
                  },
                ),
                const SizedBox(height: 12),
                Text('تعداد سفارش‌ها: ${state.total}'),
                if (state.errorMessage != null) ...[
                  const SizedBox(height: 10),
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                if (state.items.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 90),
                    child: FarmEmptyView(
                      message: 'سفارش فروشی برای نمایش وجود ندارد.',
                    ),
                  )
                else ...[
                  const SizedBox(height: 8),
                  ...state.items.map(
                    (order) => Card(
                      child: ListTile(
                        onTap: () => context.push('/seller/orders/${order.id}'),
                        leading: const Icon(Icons.inventory_2_outlined),
                        title: Text(order.orderNumber),
                        subtitle: Text(
                          '${orderStatusLabelFa(order.status)} • '
                          '${formatToman(context, order.sellerAmount)}',
                        ),
                        trailing: const Icon(Icons.chevron_right),
                      ),
                    ),
                  ),
                  if (state.totalPages > 1)
                    _Pagination(
                      page: state.page,
                      totalPages: state.totalPages,
                      onPage: (page) {
                        ref
                            .read(sellerOrderControllerProvider.notifier)
                            .loadList(page: page, status: _status);
                      },
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

class _Pagination extends StatelessWidget {
  const _Pagination({
    required this.page,
    required this.totalPages,
    required this.onPage,
  });

  final int page;
  final int totalPages;
  final ValueChanged<int> onPage;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      IconButton(
        onPressed: page > 1 ? () => onPage(page - 1) : null,
        icon: const Icon(Icons.chevron_right),
      ),
      Text('$page از $totalPages'),
      IconButton(
        onPressed: page < totalPages ? () => onPage(page + 1) : null,
        icon: const Icon(Icons.chevron_left),
      ),
    ],
  );
}

class _SellerDenied extends StatelessWidget {
  const _SellerDenied({required this.onRetry});

  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.lock_outline, size: 50),
          const SizedBox(height: 12),
          const Text(
            'برای مدیریت سفارش‌های فروش باید مالک فروشگاه تأییدشده باشید.',
            textAlign: TextAlign.center,
          ),
          TextButton(onPressed: onRetry, child: const Text('تلاش دوباره')),
        ],
      ),
    ),
  );
}
