import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_primary_action_bar.dart';
import '../../favorites/data/favorite_models.dart';
import '../../favorites/presentation/favorite_button.dart';
import '../../orders/state/order_controller.dart';
import '../../reviews/presentation/public_reviews_section.dart';
import '../data/product_models.dart';
import '../state/product_controller.dart';

class PublicProductDetailScreen extends ConsumerStatefulWidget {
  const PublicProductDetailScreen({required this.productId, super.key});

  final int productId;

  @override
  ConsumerState<PublicProductDetailScreen> createState() =>
      _PublicProductDetailScreenState();
}

class _PublicProductDetailScreenState
    extends ConsumerState<PublicProductDetailScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref
          .read(productControllerProvider.notifier)
          .loadPublicProductById(widget.productId);
    });
  }

  String _priceText(Product product) {
    final value = product.price.toStringAsFixed(0);
    return '$value ${product.currency == 'TOMAN' ? 'تومان' : product.currency}';
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(productControllerProvider);
    final orderState = ref.watch(orderControllerProvider);
    final product = state.selectedProduct;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          product?.name ??
              context.l10n.tr(fa: 'جزئیات محصول', en: 'Product details'),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          FavoriteIconButton(
            subjectType: FavoriteSubjectType.product,
            subjectId: widget.productId,
          ),
        ],
      ),
      bottomNavigationBar:
          product == null
              ? null
              : FarmPrimaryActionBar(
                onPressed:
                    orderState.isSaving
                        ? null
                        : () async {
                          final ok = await ref
                              .read(orderControllerProvider.notifier)
                              .addToCart(productId: product.id, quantity: 1);
                          if (!ok || !context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                context.l10n.tr(
                                  fa: 'محصول به سبد خرید اضافه شد.',
                                  en: 'Product added to cart.',
                                ),
                              ),
                            ),
                          );
                        },
                icon: Icons.add_shopping_cart,
                label: context.l10n.tr(
                  fa: 'افزودن به سبد خرید',
                  en: 'Add to cart',
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

          if (product == null) {
            return const Center(child: Text('محصول پیدا نشد.'));
          }

          final imageUrl = absoluteApiUrl(product.primaryImage?.publicUrl);

          return SingleChildScrollView(
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(r.s(20)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (imageUrl == null)
                          const Icon(Icons.inventory_2_outlined, size: 56)
                        else
                          ClipRRect(
                            borderRadius: BorderRadius.circular(r.s(16)),
                            child: AspectRatio(
                              aspectRatio: 16 / 9,
                              child: Image.network(
                                imageUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (_, __, ___) {
                                  return const Center(
                                    child: Icon(
                                      Icons.image_not_supported_outlined,
                                      size: 56,
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),
                        SizedBox(height: r.v(12)),
                        Text(
                          product.name,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        SizedBox(height: r.v(8)),
                        Text(
                          product.shortDescription ??
                              'توضیح کوتاه ثبت نشده است.',
                          textAlign: TextAlign.center,
                        ),
                        const Divider(height: 32),
                        _InfoRow(label: 'قیمت', value: _priceText(product)),
                        _InfoRow(
                          label: 'موجودی',
                          value: '${product.stockQuantity} ${product.unit}',
                        ),
                        _InfoRow(
                          label: 'فروشگاه',
                          value: product.storeName ?? '-',
                        ),
                        _InfoRow(
                          label: 'دسته‌بندی',
                          value: product.categoryName ?? '-',
                        ),
                        _InfoRow(
                          label: 'حداقل سفارش',
                          value: product.minOrderQuantity.toString(),
                        ),
                        if (product.description != null) ...[
                          const Divider(height: 32),
                          Text(product.description!),
                        ],
                        if (product.primaryImage != null) ...[
                          const Divider(height: 32),
                          Text(
                            'تصویر اصلی:',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          SizedBox(height: r.v(8)),
                          Text(
                            product.primaryImage!.publicUrl ??
                                product.primaryImage!.filePath,
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        PublicReviewsSection(
                          subjectType: 'product',
                          subjectId: product.id,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
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
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(label)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
