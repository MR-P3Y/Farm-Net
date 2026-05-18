import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/product_models.dart';
import '../state/product_controller.dart';

class StoreProductsScreen extends ConsumerStatefulWidget {
  const StoreProductsScreen({required this.storeSlug, super.key});

  final String storeSlug;

  @override
  ConsumerState<StoreProductsScreen> createState() =>
      _StoreProductsScreenState();
}

class _StoreProductsScreenState extends ConsumerState<StoreProductsScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref
          .read(productControllerProvider.notifier)
          .loadStoreProducts(storeSlug: widget.storeSlug);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(productControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('محصولات فروشگاه'),
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

          if (state.storeProducts.isEmpty) {
            return const Center(child: Text('این فروشگاه محصولی ندارد.'));
          }

          return ListView(
            padding: r.pagePadding(),
            children:
                state.storeProducts
                    .map(
                      (product) => Padding(
                        padding: EdgeInsets.only(bottom: r.v(12)),
                        child: _StoreProductCard(product: product),
                      ),
                    )
                    .toList(),
          );
        },
      ),
    );
  }
}

class _StoreProductCard extends StatelessWidget {
  const _StoreProductCard({required this.product});

  final Product product;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.inventory_2_outlined),
        title: Text(product.name),
        subtitle: Text('${product.price.toStringAsFixed(0)} تومان'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          context.push('/products/${product.id}');
        },
      ),
    );
  }
}
