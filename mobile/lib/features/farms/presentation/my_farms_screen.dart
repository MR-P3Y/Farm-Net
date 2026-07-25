import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';

class MyFarmsScreen extends ConsumerStatefulWidget {
  const MyFarmsScreen({super.key});

  @override
  ConsumerState<MyFarmsScreen> createState() => _MyFarmsScreenState();
}

class _MyFarmsScreenState extends ConsumerState<MyFarmsScreen> {
  List<FarmModel>? _items;
  Object? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _error = null);
    try {
      final items = await ref.read(farmRepositoryProvider).farms();
      if (mounted) setState(() => _items = items);
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _create() async {
    final name = TextEditingController();
    final description = TextEditingController();
    final area = TextEditingController();
    final submit = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('مزرعه جدید'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: name,
                    decoration: const InputDecoration(labelText: 'نام مزرعه *'),
                  ),
                  TextField(
                    controller: description,
                    decoration: const InputDecoration(labelText: 'توضیحات'),
                  ),
                  TextField(
                    controller: area,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'مساحت کل (متر مربع)',
                    ),
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
                onPressed: () => Navigator.pop(context, true),
                child: const Text('ایجاد'),
              ),
            ],
          ),
    );
    if (submit != true || name.text.trim().isEmpty) return;
    try {
      await ref.read(farmRepositoryProvider).createFarm({
        'name': name.text.trim(),
        'description':
            description.text.trim().isEmpty ? null : description.text.trim(),
        'declared_area_sqm': double.tryParse(area.text),
      });
      await _load();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: const FarmAppBar(title: 'مزرعه‌های من'),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: _create,
      icon: const Icon(Icons.add),
      label: const Text('مزرعه جدید'),
    ),
    body:
        _error != null
            ? _ErrorState(error: _error!, onRetry: _load)
            : _items == null
            ? const FarmLoadingView()
            : _items!.isEmpty
            ? const FarmEmptyView(message: 'هنوز مزرعه‌ای ثبت نشده است')
            : RefreshIndicator(
              onRefresh: _load,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: _items!.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final farm = _items![index];
                  return Card(
                    child: ListTile(
                      leading: const CircleAvatar(
                        child: Icon(Icons.agriculture_outlined),
                      ),
                      title: Text(farm.name),
                      subtitle: Text(
                        farm.declaredAreaSqm == null
                            ? 'مساحت کل ثبت نشده'
                            : '${farm.declaredAreaSqm} متر مربع',
                      ),
                      trailing: const Icon(Icons.chevron_left),
                      onTap:
                          () => context.push('/farms/${farm.id}', extra: farm),
                    ),
                  );
                },
              ),
            ),
  );
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(error.toString(), textAlign: TextAlign.center),
        TextButton(onPressed: onRetry, child: const Text('تلاش دوباره')),
      ],
    ),
  );
}
