import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/order_models.dart';
import '../state/order_controller.dart';

class CartScreen extends ConsumerStatefulWidget {
  const CartScreen({super.key});

  @override
  ConsumerState<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends ConsumerState<CartScreen> {
  final _addressController = TextEditingController(text: 'Test address');
  final _phoneController = TextEditingController(text: '09120000000');
  final _postalCodeController = TextEditingController(text: '1234567890');

  bool _loaded = false;

  @override
  void dispose() {
    _addressController.dispose();
    _phoneController.dispose();
    _postalCodeController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(orderControllerProvider.notifier).loadCart();
    });
  }

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  Future<void> _checkout() async {
    final ok = await ref
        .read(orderControllerProvider.notifier)
        .checkout(
          CheckoutInput(
            idempotencyKey:
                'mobile-${DateTime.now().microsecondsSinceEpoch.toString()}',
            buyerNote: 'Mobile checkout',
            shippingAddress: _addressController.text.trim(),
            shippingPhone: _phoneController.text.trim(),
            shippingPostalCode: _postalCodeController.text.trim(),
          ),
        );

    if (!ok || !mounted) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('سفارش با موفقیت ثبت شد.')));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(orderControllerProvider);
    final cart = state.cart;

    return Scaffold(
      appBar: AppBar(
        title: const Text('سبد خرید'),
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

          if (cart == null) {
            return const Center(child: Text('سبد خرید در دسترس نیست.'));
          }

          return RefreshIndicator(
            onRefresh: () {
              return ref.read(orderControllerProvider.notifier).loadCart();
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
                if (cart.items.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('سبد خرید خالی است.')),
                  )
                else ...[
                  ...cart.items.map(
                    (item) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: _CartItemCard(item: item),
                    ),
                  ),
                  const Divider(height: 32),
                  TextField(
                    controller: _addressController,
                    decoration: const InputDecoration(
                      labelText: 'آدرس ارسال',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                  TextField(
                    controller: _phoneController,
                    decoration: const InputDecoration(
                      labelText: 'شماره تماس',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                  TextField(
                    controller: _postalCodeController,
                    decoration: const InputDecoration(
                      labelText: 'کد پستی',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  SizedBox(height: r.v(16)),
                  Text(
                    'جمع کل: ${_price(cart.subtotalAmount)}',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  SizedBox(height: r.v(16)),
                  FilledButton.icon(
                    onPressed: state.isSaving ? null : _checkout,
                    icon: const Icon(Icons.shopping_bag_outlined),
                    label: const Text('ثبت سفارش'),
                  ),
                  SizedBox(height: r.v(8)),
                  OutlinedButton.icon(
                    onPressed:
                        state.isSaving
                            ? null
                            : () {
                              ref
                                  .read(orderControllerProvider.notifier)
                                  .clearCart();
                            },
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('پاک کردن سبد'),
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

class _CartItemCard extends ConsumerWidget {
  const _CartItemCard({required this.item});

  final CartItem item;

  String _price(num value) => '${value.toStringAsFixed(0)} تومان';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.inventory_2_outlined),
        title: Text(item.productNameSnapshot),
        subtitle: Text(
          'تعداد: ${item.quantity}\nقیمت: ${_price(item.lineTotal)}',
        ),
        isThreeLine: true,
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            final controller = ref.read(orderControllerProvider.notifier);

            if (value == 'plus') {
              controller.updateCartItem(
                itemId: item.id,
                quantity: item.quantity + 1,
              );
            }

            if (value == 'minus' && item.quantity > 1) {
              controller.updateCartItem(
                itemId: item.id,
                quantity: item.quantity - 1,
              );
            }

            if (value == 'delete') {
              controller.deleteCartItem(item.id);
            }
          },
          itemBuilder:
              (_) => const [
                PopupMenuItem(value: 'plus', child: Text('افزایش تعداد')),
                PopupMenuItem(value: 'minus', child: Text('کاهش تعداد')),
                PopupMenuItem(value: 'delete', child: Text('حذف')),
              ],
        ),
      ),
    );
  }
}
