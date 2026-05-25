import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_product_models.dart';
import '../state/admin_product_controller.dart';

class AdminProductsPage extends ConsumerStatefulWidget {
  const AdminProductsPage({super.key});

  @override
  ConsumerState<AdminProductsPage> createState() => _AdminProductsPageState();
}

class _AdminProductsPageState extends ConsumerState<AdminProductsPage> {
  final _searchController = TextEditingController();
  bool _loaded = false;
  String? _statusFilter;

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
      ref.read(adminProductControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() async {
    await ref
        .read(adminProductControllerProvider.notifier)
        .load(status: _statusFilter, q: _searchController.text.trim());
  }

  Future<void> _openDetail(AdminProduct item) async {
    await ref.read(adminProductControllerProvider.notifier).loadDetail(item.id);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _ProductDetailDialog(productId: item.id),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminProductControllerProvider);

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
                    'محصولات',
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
                    width: r.isCompact ? double.infinity : 320,
                    child: TextField(
                      controller: _searchController,
                      decoration: const InputDecoration(
                        labelText: 'جستجو نام، slug یا SKU',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _reload(),
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 260,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _statusFilter,
                      decoration: const InputDecoration(
                        labelText: 'وضعیت',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'draft',
                          child: Text('پیش‌نویس'),
                        ),
                        DropdownMenuItem(
                          value: 'published',
                          child: Text('منتشر شده'),
                        ),
                        DropdownMenuItem(
                          value: 'unpublished',
                          child: Text('منتشر نشده'),
                        ),
                        DropdownMenuItem(
                          value: 'suspended',
                          child: Text('تعلیق شده'),
                        ),
                        DropdownMenuItem(
                          value: 'archived',
                          child: Text('بایگانی شده'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    height: 56,
                    child: FilledButton.icon(
                      onPressed: _reload,
                      icon: const Icon(Icons.search),
                      label: const Text('جستجو'),
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
                        : _ProductTable(
                          items: state.items,
                          onOpen: _openDetail,
                        ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProductTable extends StatelessWidget {
  const _ProductTable({required this.items, required this.onOpen});

  final List<AdminProduct> items;
  final ValueChanged<AdminProduct> onOpen;

  String _priceText(AdminProduct product) {
    final value = product.price.toStringAsFixed(0);
    return '$value ${product.currency == 'TOMAN' ? 'تومان' : product.currency}';
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'draft':
        return 'پیش‌نویس';
      case 'published':
        return 'منتشر شده';
      case 'unpublished':
        return 'منتشر نشده';
      case 'suspended':
        return 'تعلیق شده';
      case 'archived':
        return 'بایگانی شده';
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'محصولی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('نام')),
          DataColumn(label: Text('فروشگاه')),
          DataColumn(label: Text('قیمت')),
          DataColumn(label: Text('وضعیت')),
          DataColumn(label: Text('عملیات')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.name)),
                  DataCell(Text(item.storeName ?? '-')),
                  DataCell(Text(_priceText(item))),
                  DataCell(Text(_statusLabel(item.status))),
                  DataCell(
                    TextButton(
                      onPressed: () => onOpen(item),
                      child: const Text('بررسی'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }
}

class _ProductDetailDialog extends ConsumerStatefulWidget {
  const _ProductDetailDialog({required this.productId});

  final int productId;

  @override
  ConsumerState<_ProductDetailDialog> createState() =>
      _ProductDetailDialogState();
}

class _ProductDetailDialogState extends ConsumerState<_ProductDetailDialog> {
  final _noteController = TextEditingController();

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _updateStatus(String status) async {
    final ok = await ref
        .read(adminProductControllerProvider.notifier)
        .updateStatus(
          productId: widget.productId,
          status: status,
          note: _noteController.text.trim(),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  String _priceText(AdminProduct product) {
    final value = product.price.toStringAsFixed(0);
    return '$value ${product.currency == 'TOMAN' ? 'تومان' : product.currency}';
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminProductControllerProvider);
    final product = state.selected;

    if (product == null) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    final canSuspend =
        product.status == 'published' || product.status == 'unpublished';
    final canRestore = product.status == 'suspended';

    return AlertDialog(
      title: Text('بررسی محصول #${product.id}'),
      content: SizedBox(
        width: 820,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.72,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('نام: ${product.name}'),
                const SizedBox(height: 8),
                Text('Slug: ${product.slug}'),
                const SizedBox(height: 8),
                Text('SKU: ${product.sku ?? '-'}'),
                const SizedBox(height: 8),
                Text('فروشگاه: ${product.storeName ?? '-'}'),
                const SizedBox(height: 8),
                Text(
                  'مالک: ${product.ownerEmail ?? product.ownerPhone ?? '-'}',
                ),
                const SizedBox(height: 8),
                Text('وضعیت: ${product.status}'),
                const SizedBox(height: 8),
                Text('قیمت: ${_priceText(product)}'),
                const SizedBox(height: 8),
                Text('موجودی: ${product.stockQuantity} ${product.unit}'),
                const SizedBox(height: 8),
                Text('دسته‌بندی: ${product.categoryName ?? '-'}'),
                const SizedBox(height: 8),
                Text('توضیح کوتاه: ${product.shortDescription ?? '-'}'),
                const SizedBox(height: 8),
                Text('توضیحات: ${product.description ?? '-'}'),
                const Divider(height: 28),
                Text('تصاویر', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                if (product.images.isEmpty)
                  const Text('تصویری ثبت نشده است.')
                else
                  ...product.images.map(
                    (image) => ListTile(
                      dense: true,
                      leading: Icon(
                        image.isPrimary ? Icons.star : Icons.image_outlined,
                      ),
                      title: Text(image.filePath),
                      subtitle: Text(
                        'sort=${image.sortOrder} / primary=${image.isPrimary}',
                      ),
                    ),
                  ),
                const Divider(height: 28),
                Text(
                  'تاریخچه وضعیت',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                if (product.statusHistory.isEmpty)
                  const Text('تاریخچه‌ای ثبت نشده است.')
                else
                  ...product.statusHistory.map(
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
        if (canSuspend)
          OutlinedButton.icon(
            onPressed: state.isSaving ? null : () => _updateStatus('suspended'),
            icon: const Icon(Icons.block),
            label: const Text('تعلیق'),
          ),
        if (canRestore) ...[
          OutlinedButton.icon(
            onPressed:
                state.isSaving ? null : () => _updateStatus('unpublished'),
            icon: const Icon(Icons.visibility_off_outlined),
            label: const Text('بازگردانی بدون انتشار'),
          ),
          FilledButton.icon(
            onPressed: state.isSaving ? null : () => _updateStatus('published'),
            icon: const Icon(Icons.restore),
            label: const Text('بازگردانی و انتشار'),
          ),
        ],
      ],
    );
  }
}
