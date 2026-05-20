import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/admin_loading_view.dart';
import '../state/admin_commission_controller.dart';

class AdminCommissionPage extends ConsumerStatefulWidget {
  const AdminCommissionPage({super.key});

  @override
  ConsumerState<AdminCommissionPage> createState() =>
      _AdminCommissionPageState();
}

class _AdminCommissionPageState extends ConsumerState<AdminCommissionPage> {
  final _percentController = TextEditingController();
  final _descriptionController = TextEditingController();
  bool _loaded = false;
  bool _filled = false;

  @override
  void dispose() {
    _percentController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminCommissionControllerProvider.notifier).load();
    });
  }

  void _fillOnce() {
    if (_filled) return;

    final setting = ref.watch(adminCommissionControllerProvider).setting;
    if (setting == null) return;

    _filled = true;
    _percentController.text = setting.percent.toString();
    _descriptionController.text = setting.description ?? '';
  }

  Future<void> _save() async {
    final percent = num.tryParse(_percentController.text.trim()) ?? -1;

    final ok = await ref
        .read(adminCommissionControllerProvider.notifier)
        .update(
          percent: percent,
          description: _descriptionController.text.trim(),
        );

    if (!ok || !mounted) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('درصد کمیسیون ذخیره شد.')));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminCommissionControllerProvider);
    _fillOnce();

    return Padding(
      padding: const EdgeInsets.all(24),
      child:
          state.isLoading
              ? const AdminLoadingView()
              : Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 640),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'تنظیمات کمیسیون',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 12),
                          if (state.setting != null)
                            Text(
                              'وضعیت: ${state.setting!.status} / پیش‌فرض: ${state.setting!.isDefault}',
                            ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: _percentController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'درصد کمیسیون',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _descriptionController,
                            maxLines: 3,
                            decoration: const InputDecoration(
                              labelText: 'توضیحات',
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
                          const SizedBox(height: 18),
                          FilledButton.icon(
                            onPressed: state.isSaving ? null : _save,
                            icon: const Icon(Icons.save_outlined),
                            label: const Text('ذخیره'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
    );
  }
}
