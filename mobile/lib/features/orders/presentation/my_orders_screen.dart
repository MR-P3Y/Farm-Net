import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/order_models.dart';
import '../state/order_controller.dart';

class MyOrdersScreen extends ConsumerStatefulWidget {
  const MyOrdersScreen({super.key});

  @override
  ConsumerState<MyOrdersScreen> createState() => _MyOrdersScreenState();
}

class _MyOrdersScreenState extends ConsumerState<MyOrdersScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(orderControllerProvider.notifier).loadMyOrders();
    });
  }

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(orderControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('سفارش‌های من'),
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

          return RefreshIndicator(
            onRefresh: () {
              return ref.read(orderControllerProvider.notifier).loadMyOrders();
            },
            child: ListView(
              padding: r.pagePadding(),
              children: [
                if (state.errorMessage != null) ...[
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                ],
                if (state.orders.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('هنوز سفارشی ثبت نشده است.')),
                  )
                else
                  ...state.orders.map(
                    (order) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: _OrderCard(
                        order: order,
                        priceText: _price(order.totalAmount),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _OrderCard extends StatelessWidget {
  const _OrderCard({required this.order, required this.priceText});

  final Order order;
  final String priceText;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.receipt_long_outlined),
        title: Text(order.orderNumber),
        subtitle: Text(
          'وضعیت: ${order.status}\nپرداخت: ${order.paymentStatus}\nمبلغ: $priceText',
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          context.push('/orders/${order.id}');
        },
      ),
    );
  }
}
