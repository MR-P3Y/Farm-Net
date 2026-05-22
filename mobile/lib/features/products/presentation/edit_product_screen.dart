import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/product_models.dart';
import '../state/product_controller.dart';

class EditProductScreen extends ConsumerStatefulWidget {
  const EditProductScreen({
    required this.storeId,
    required this.product,
    super.key,
  });

  final int storeId;
  final Product? product;

  @override
  ConsumerState<EditProductScreen> createState() => _EditProductScreenState();
}

class _EditProductScreenState extends ConsumerState<EditProductScreen> {
  final _nameController = TextEditingController();
  final _slugController = TextEditingController();
  final _shortDescriptionController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _skuController = TextEditingController();
  final _priceController = TextEditingController(text: '250000');
  final _stockController = TextEditingController(text: '100');

  String _unit = 'kg';
  String? _productImageMediaFileKey;
  bool _filled = false;

  @override
  void dispose() {
    _nameController.dispose();
    _slugController.dispose();
    _shortDescriptionController.dispose();
    _descriptionController.dispose();
    _skuController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    super.dispose();
  }

  void _fillOnce() {
    if (_filled) return;
    _filled = true;

    final product = widget.product;

    if (product == null) {
      final now = DateTime.now().millisecondsSinceEpoch;
      _nameController.text = 'محصول تست فارم نت';
      _slugController.text = 'farmnet-product-$now';
      _shortDescriptionController.text = 'توضیح کوتاه محصول';
      _descriptionController.text = 'توضیح کامل محصول تستی فارم نت';
      _skuController.text = 'SKU-$now';
      return;
    }

    _nameController.text = product.name;
    _slugController.text = product.slug;
    _shortDescriptionController.text = product.shortDescription ?? '';
    _descriptionController.text = product.description ?? '';
    _skuController.text = product.sku ?? '';
    _priceController.text = product.price.toStringAsFixed(0);
    _stockController.text = product.stockQuantity.toString();
    _unit = product.unit;
  }

  Future<void> _save() async {
    final controller = ref.read(productControllerProvider.notifier);
    final price = num.tryParse(_priceController.text.trim()) ?? 0;
    final stock = int.tryParse(_stockController.text.trim()) ?? 0;
    final product = widget.product;

    final ok =
        product == null
            ? await controller.createProduct(
              storeId: widget.storeId,
              input: ProductCreateInput(
                name: _nameController.text.trim(),
                slug: _slugController.text.trim(),
                shortDescription: _shortDescriptionController.text.trim(),
                description: _descriptionController.text.trim(),
                sku: _skuController.text.trim(),
                price: price,
                stockQuantity: stock,
                unit: _unit,
              ),
            )
            : await controller.updateProduct(
              storeId: widget.storeId,
              productId: product.id,
              input: ProductUpdateInput(
                name: _nameController.text.trim(),
                slug: _slugController.text.trim(),
                shortDescription: _shortDescriptionController.text.trim(),
                description: _descriptionController.text.trim(),
                sku: _skuController.text.trim(),
                price: price,
                stockQuantity: stock,
                unit: _unit,
              ),
            );

    if (!ok || !mounted) return;

    final mediaFileKey = _productImageMediaFileKey;
    final savedProduct =
        ref.read(productControllerProvider).selectedProduct ?? product;

    if (mediaFileKey != null && savedProduct != null) {
      final imageOk = await controller.createProductImage(
        storeId: widget.storeId,
        productId: savedProduct.id,
        input: ProductImageCreateInput(
          mediaFileKey: mediaFileKey,
          altText: _nameController.text.trim(),
          sortOrder: 0,
          isPrimary: true,
        ),
      );

      if (!imageOk || !mounted) return;
    }

    await ref
        .read(productControllerProvider.notifier)
        .loadMyProducts(storeId: widget.storeId);

    if (!mounted) return;
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    _fillOnce();
    final state = ref.watch(productControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.product == null ? 'افزودن محصول' : 'ویرایش محصول'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
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
                        TextField(
                          controller: _nameController,
                          decoration: const InputDecoration(
                            labelText: 'نام محصول',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _slugController,
                          decoration: const InputDecoration(
                            labelText: 'Slug انگلیسی',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _shortDescriptionController,
                          decoration: const InputDecoration(
                            labelText: 'توضیح کوتاه',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _descriptionController,
                          maxLines: 4,
                          decoration: const InputDecoration(
                            labelText: 'توضیحات کامل',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _skuController,
                          decoration: const InputDecoration(
                            labelText: 'SKU',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _priceController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'قیمت به تومان',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _stockController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'موجودی',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<String>(
                          value: _unit,
                          decoration: const InputDecoration(
                            labelText: 'واحد',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'kg',
                              child: Text('کیلوگرم'),
                            ),
                            DropdownMenuItem(value: 'gram', child: Text('گرم')),
                            DropdownMenuItem(
                              value: 'liter',
                              child: Text('لیتر'),
                            ),
                            DropdownMenuItem(
                              value: 'ml',
                              child: Text('میلی‌لیتر'),
                            ),
                            DropdownMenuItem(
                              value: 'piece',
                              child: Text('عدد'),
                            ),
                            DropdownMenuItem(
                              value: 'pack',
                              child: Text('بسته'),
                            ),
                            DropdownMenuItem(value: 'bag', child: Text('کیسه')),
                            DropdownMenuItem(value: 'ton', child: Text('تن')),
                            DropdownMenuItem(
                              value: 'meter',
                              child: Text('متر'),
                            ),
                            DropdownMenuItem(
                              value: 'other',
                              child: Text('سایر'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _unit = value);
                          },
                        ),
                        SizedBox(height: r.v(16)),
                        MediaUploadButton(
                          label: 'آپلود تصویر محصول',
                          purpose: 'product_image',
                          visibility: 'public',
                          allowedExtensions: const [
                            'jpg',
                            'jpeg',
                            'png',
                            'webp',
                          ],
                          onUploaded: (media) {
                            setState(() {
                              _productImageMediaFileKey = media.fileKey;
                            });
                          },
                        ),
                        if (_productImageMediaFileKey != null) ...[
                          SizedBox(height: r.v(8)),
                          Text(
                            'تصویر آپلود شد: $_productImageMediaFileKey',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                        if (state.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        FilledButton(
                          onPressed: state.isSaving ? null : _save,
                          child:
                              state.isSaving
                                  ? const SizedBox.square(
                                    dimension: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                  : const Text('ذخیره محصول'),
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
