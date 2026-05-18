import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../stores/state/store_controller.dart';
import '../data/product_models.dart';
import '../state/product_controller.dart';
import 'edit_product_screen.dart';

class MyProductsScreen extends ConsumerStatefulWidget {
  const MyProductsScreen({super.key});

  @override
  ConsumerState<MyProductsScreen> createState() => _MyProductsScreenState();
}

class _MyProductsScreenState extends ConsumerState<MyProductsScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() async {
      await ref.read(storeControllerProvider.notifier).loadMyStore();

      final store = ref.read(storeControllerProvider).myStore;
      if (store != null) {
        await ref
            .read(productControllerProvider.notifier)
            .loadMyProducts(storeId: store.id);
      }
    });
  }

  Future<void> _refresh() async {
    final store = ref.read(storeControllerProvider).myStore;
    if (store == null) return;

    await ref
        .read(productControllerProvider.notifier)
        .loadMyProducts(storeId: store.id);
  }

  Future<void> _togglePublish(Product product) async {
    final store = ref.read(storeControllerProvider).myStore;
    if (store == null) return;

    final controller = ref.read(productControllerProvider.notifier);

    if (product.status == 'published') {
      await controller.unpublishProduct(
        storeId: store.id,
        productId: product.id,
      );
    } else {
      await controller.publishProduct(storeId: store.id, productId: product.id);
    }
  }

  @override
  Widget build(BuildContext context) {
    final storeState = ref.watch(storeControllerProvider);
    final productState = ref.watch(productControllerProvider);
    final store = storeState.myStore;

    return Scaffold(
      appBar: AppBar(
        title: const Text('محصولات من'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          if (store != null && store.status == 'approved')
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder:
                        (_) =>
                            EditProductScreen(storeId: store.id, product: null),
                  ),
                );
              },
            ),
        ],
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (storeState.isLoading || productState.isLoading) {
            return const FarmLoadingView();
          }

          if (store == null) {
            return const Center(
              child: Text('ابتدا باید فروشگاه خود را بسازید.'),
            );
          }

          if (store.status != 'approved') {
            return Center(
              child: Text(
                'برای مدیریت محصول، فروشگاه شما باید تأیید شده باشد.\n'
                'وضعیت فعلی: ${store.status}',
                textAlign: TextAlign.center,
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView(
              padding: r.pagePadding(),
              children: [
                if (productState.errorMessage != null) ...[
                  Text(
                    productState.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                  SizedBox(height: r.v(12)),
                ],
                if (productState.myProducts.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: Text('هنوز محصولی ثبت نکرده‌اید.')),
                  )
                else
                  ...productState.myProducts.map(
                    (product) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: Card(
                        child: ListTile(
                          leading: const Icon(Icons.inventory_2_outlined),
                          title: Text(product.name),
                          subtitle: Text(
                            'وضعیت: ${product.status ?? '-'}\n'
                            'قیمت: ${product.price.toStringAsFixed(0)} تومان',
                          ),
                          isThreeLine: true,
                          trailing: PopupMenuButton<String>(
                            onSelected: (value) {
                              if (value == 'edit') {
                                Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder:
                                        (_) => EditProductScreen(
                                          storeId: store.id,
                                          product: product,
                                        ),
                                  ),
                                );
                              }

                              if (value == 'publish') {
                                _togglePublish(product);
                              }
                            },
                            itemBuilder:
                                (_) => [
                                  const PopupMenuItem(
                                    value: 'edit',
                                    child: Text('ویرایش'),
                                  ),
                                  PopupMenuItem(
                                    value: 'publish',
                                    child: Text(
                                      product.status == 'published'
                                          ? 'عدم انتشار'
                                          : 'انتشار',
                                    ),
                                  ),
                                ],
                          ),
                        ),
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
