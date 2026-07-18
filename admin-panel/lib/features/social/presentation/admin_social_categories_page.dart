import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_social_api.dart';
import '../data/admin_social_models.dart';
import '../data/admin_social_repository.dart';

class AdminSocialCategoriesPage extends ConsumerStatefulWidget {
  const AdminSocialCategoriesPage({super.key});
  @override
  ConsumerState<AdminSocialCategoriesPage> createState() => _State();
}

class _State extends ConsumerState<AdminSocialCategoriesPage> {
  final search = TextEditingController();
  bool loading = true;
  String? error;
  List<AdminSocialCategory> items = const [];

  @override
  void initState() {
    super.initState();
    Future.microtask(load);
  }

  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  Future<void> load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final result = await ref
          .read(adminSocialRepositoryProvider)
          .categories(q: search.text);
      if (mounted) setState(() => items = result);
    } on AdminSocialApiException catch (e) {
      if (mounted) setState(() => error = e.error.message);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> edit([AdminSocialCategory? item]) async {
    final code = TextEditingController(text: item?.code);
    final title = TextEditingController(text: item?.title);
    final description = TextEditingController(text: item?.description);
    final order = TextEditingController(text: '${item?.sortOrder ?? 100}');
    bool active = item?.isActive ?? true;
    final saved = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: Text(
                    item == null ? 'دسته اجتماعی جدید' : 'ویرایش دسته اجتماعی',
                  ),
                  content: SizedBox(
                    width: 500,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        TextField(
                          controller: code,
                          decoration: const InputDecoration(
                            labelText: 'کد انگلیسی',
                          ),
                        ),
                        TextField(
                          controller: title,
                          decoration: const InputDecoration(labelText: 'عنوان'),
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
                          onChanged: (v) => setDialogState(() => active = v),
                        ),
                      ],
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
                              .read(adminSocialRepositoryProvider)
                              .saveCategory(
                                id: item?.id,
                                data: {
                                  'code': code.text.trim(),
                                  'title': title.text.trim(),
                                  'description':
                                      description.text.trim().isEmpty
                                          ? null
                                          : description.text.trim(),
                                  'sort_order': int.tryParse(order.text) ?? 100,
                                  'is_active': active,
                                },
                              );
                          if (context.mounted) Navigator.pop(context, true);
                        } on AdminSocialApiException catch (e) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(e.error.message)),
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
    code.dispose();
    title.dispose();
    description.dispose();
    order.dispose();
    if (saved == true) await load();
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Text(
              'دسته‌بندی جامعه',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed: () => edit(),
              icon: const Icon(Icons.add),
              label: const Text('دسته جدید'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        TextField(
          controller: search,
          onSubmitted: (_) => load(),
          decoration: InputDecoration(
            labelText: 'جستجو',
            border: const OutlineInputBorder(),
            suffixIcon: IconButton(
              onPressed: load,
              icon: const Icon(Icons.search),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Expanded(child: body()),
      ],
    ),
  );

  Widget body() {
    if (loading) return const Center(child: CircularProgressIndicator());
    if (error != null) return Center(child: Text(error!));
    if (items.isEmpty) {
      return const Center(child: Text('دسته‌ای ثبت نشده است.'));
    }
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          child: ListTile(
            leading: Icon(
              item.isActive
                  ? Icons.forum_outlined
                  : Icons.comments_disabled_outlined,
            ),
            title: Text(item.title),
            subtitle: Text(
              '${item.code} • ترتیب ${item.sortOrder} • ${item.postsCount} پست',
            ),
            trailing: IconButton(
              onPressed: () => edit(item),
              icon: const Icon(Icons.edit_outlined),
            ),
          ),
        );
      },
    );
  }
}
