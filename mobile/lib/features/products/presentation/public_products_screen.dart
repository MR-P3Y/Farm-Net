import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/product_models.dart';
import '../state/product_controller.dart';

class PublicProductsScreen extends ConsumerStatefulWidget {
  const PublicProductsScreen({super.key});

  @override
  ConsumerState<PublicProductsScreen> createState() =>
      _PublicProductsScreenState();
}

class _PublicProductsScreenState extends ConsumerState<PublicProductsScreen> {
  final _searchController = TextEditingController();
  bool _loaded = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(productControllerProvider.notifier).loadPublicProducts();
    });
  }

  Future<void> _search() {
    return ref
        .read(productControllerProvider.notifier)
        .loadPublicProducts(q: _searchController.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(productControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('محصولات'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return RefreshIndicator(
            onRefresh:
                () =>
                    ref
                        .read(productControllerProvider.notifier)
                        .loadPublicProducts(),
            child: ListView(
              padding: r.pagePadding(),
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _searchController,
                        decoration: const InputDecoration(
                          labelText: 'جستجوی محصول',
                          border: OutlineInputBorder(),
                        ),
                        onSubmitted: (_) => _search(),
                      ),
                    ),
                    SizedBox(width: r.s(8)),
                    FilledButton.icon(
                      onPressed: _search,
                      icon: const Icon(Icons.search),
                      label: const Text('جستجو'),
                    ),
                  ],
                ),
                if (state.errorMessage != null) ...[
                  SizedBox(height: r.v(12)),
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                SizedBox(height: r.v(16)),
                if (state.isLoading)
                  const FarmLoadingView()
                else if (state.publicProducts.isEmpty)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Text('محصولی برای نمایش وجود ندارد.'),
                    ),
                  )
                else
                  ...state.publicProducts.map(
                    (product) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: _ProductCard(product: product),
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

class _ProductCard extends StatelessWidget {
  const _ProductCard({required this.product});

  final Product product;

  String _priceText(Product product) {
    final value = product.price.toStringAsFixed(0);
    return '$value ${product.currency == 'TOMAN' ? 'تومان' : product.currency}';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.inventory_2_outlined),
        title: Text(product.name),
        subtitle: Text('${product.storeName ?? '-'}\n${_priceText(product)}'),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          context.push('/products/${product.id}');
        },
      ),
    );
  }
}
