import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_product_api.dart';
import '../data/admin_product_models.dart';
import '../data/admin_product_repository.dart';

class AdminProductCategoriesPage extends ConsumerStatefulWidget {
  const AdminProductCategoriesPage({super.key});

  @override
  ConsumerState<AdminProductCategoriesPage> createState() =>
      _AdminProductCategoriesPageState();
}

class _AdminProductCategoriesPageState
    extends ConsumerState<AdminProductCategoriesPage> {
  final _search = TextEditingController();
  bool _loading = true;
  String? _error;
  List<AdminProductCategory> _items = const [];

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await ref
          .read(adminProductRepositoryProvider)
          .listCategories(q: _search.text);
      if (mounted) setState(() => _items = items);
    } on AdminProductApiException catch (error) {
      if (mounted) setState(() => _error = error.error.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _edit([AdminProductCategory? item]) async {
    final name = TextEditingController(text: item?.name);
    final slug = TextEditingController(text: item?.slug);
    final description = TextEditingController(text: item?.description);
    final order = TextEditingController(text: '${item?.sortOrder ?? 0}');
    int? parentId = item?.parentId;
    bool active = item?.isActive ?? true;
    final saved = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: Text(
                    item == null ? 'دسته‌بندی جدید' : 'ویرایش دسته‌بندی',
                  ),
                  content: SizedBox(
                    width: 520,
                    child: SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          TextField(
                            controller: name,
                            decoration: const InputDecoration(labelText: 'نام'),
                          ),
                          TextField(
                            controller: slug,
                            decoration: const InputDecoration(
                              labelText: 'Slug انگلیسی',
                            ),
                          ),
                          DropdownButtonFormField<int?>(
                            initialValue: parentId,
                            decoration: const InputDecoration(
                              labelText: 'دسته والد',
                            ),
                            items: [
                              const DropdownMenuItem<int?>(
                                value: null,
                                child: Text('بدون والد'),
                              ),
                              ..._items
                                  .where((x) => x.id != item?.id)
                                  .map(
                                    (x) => DropdownMenuItem<int?>(
                                      value: x.id,
                                      child: Text(x.name),
                                    ),
                                  ),
                            ],
                            onChanged:
                                (value) =>
                                    setDialogState(() => parentId = value),
                          ),
                          TextField(
                            controller: description,
                            maxLines: 3,
                            decoration: const InputDecoration(
                              labelText: 'توضیحات',
                            ),
                          ),
                          TextField(
                            controller: order,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'ترتیب نمایش',
                            ),
                          ),
                          SwitchListTile(
                            value: active,
                            title: const Text('فعال'),
                            onChanged:
                                (value) => setDialogState(() => active = value),
                          ),
                        ],
                      ),
                    ),
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('انصراف'),
                    ),
                    FilledButton(
                      onPressed: () async {
                        try {
                          await ref
                              .read(adminProductRepositoryProvider)
                              .saveCategory(
                                id: item?.id,
                                data: {
                                  'name': name.text.trim(),
                                  'slug': slug.text.trim(),
                                  'description':
                                      description.text.trim().isEmpty
                                          ? null
                                          : description.text.trim(),
                                  'parent_id': parentId,
                                  'sort_order': int.tryParse(order.text) ?? 0,
                                  'is_active': active,
                                },
                              );
                          if (context.mounted) Navigator.pop(context, true);
                        } on AdminProductApiException catch (error) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(error.error.message)),
                            );
                          }
                        }
                      },
                      child: const Text('ذخیره'),
                    ),
                  ],
                ),
          ),
    );
    name.dispose();
    slug.dispose();
    description.dispose();
    order.dispose();
    if (saved == true) await _load();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'دسته‌بندی محصولات',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              FilledButton.icon(
                onPressed: () => _edit(),
                icon: const Icon(Icons.add),
                label: const Text('دسته جدید'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _search,
            decoration: InputDecoration(
              labelText: 'جستجوی دسته‌بندی',
              border: const OutlineInputBorder(),
              suffixIcon: IconButton(
                onPressed: _load,
                icon: const Icon(Icons.search),
              ),
            ),
            onSubmitted: (_) => _load(),
          ),
          const SizedBox(height: 16),
          Expanded(child: _body()),
        ],
      ),
    );
  }

  Widget _body() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text(_error!));
    if (_items.isEmpty) {
      return const Center(child: Text('دسته‌بندی‌ای وجود ندارد.'));
    }
    final names = {for (final item in _items) item.id: item.name};
    return ListView.builder(
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final item = _items[index];
        return Card(
          child: ListTile(
            leading: Icon(
              item.isActive ? Icons.folder : Icons.folder_off_outlined,
            ),
            title: Text(item.name),
            subtitle: Text(
              '${item.slug} • والد: ${names[item.parentId] ?? '-'} • محصول: ${item.productsCount} • فرزند: ${item.childrenCount}',
            ),
            trailing: IconButton(
              onPressed: () => _edit(item),
              icon: const Icon(Icons.edit_outlined),
            ),
          ),
        );
      },
    );
  }
}
