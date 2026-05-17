import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../profile/state/profile_controller.dart';
import '../state/store_controller.dart';
import 'edit_store_screen.dart';

class MyStoreScreen extends ConsumerStatefulWidget {
  const MyStoreScreen({super.key});

  @override
  ConsumerState<MyStoreScreen> createState() => _MyStoreScreenState();
}

class _MyStoreScreenState extends ConsumerState<MyStoreScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(storeControllerProvider.notifier).loadMyStore();
      ref.read(profileControllerProvider.notifier).load();
    });
  }

  Future<void> _submit() async {
    final ok = await ref.read(storeControllerProvider.notifier).submitMyStore();

    if (!ok || !mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فروشگاه برای بررسی ارسال شد.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(storeControllerProvider);
    final store = state.myStore;

    return Scaffold(
      appBar: AppBar(
        title: const Text('فروشگاه من'),
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
                        Icon(
                          store == null
                              ? Icons.add_business_outlined
                              : Icons.storefront_outlined,
                          size: r.s(56),
                        ),
                        SizedBox(height: r.v(12)),
                        Text(
                          store == null
                              ? 'هنوز فروشگاهی ثبت نکرده‌اید'
                              : store.name,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        SizedBox(height: r.v(12)),
                        if (store != null) ...[
                          _InfoRow(label: 'وضعیت', value: store.status ?? '-'),
                          _InfoRow(label: 'شناسه', value: store.id.toString()),
                          _InfoRow(label: 'اسلاگ', value: store.slug),
                          _InfoRow(label: 'نوع', value: store.storeType),
                          _InfoRow(label: 'آدرس', value: store.address ?? '-'),
                          _InfoRow(
                            label: 'یادداشت ادمین',
                            value: store.adminNote ?? '-',
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
                        SizedBox(height: r.v(24)),
                        FilledButton.icon(
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => EditStoreScreen(store: store),
                              ),
                            );
                          },
                          icon: Icon(
                            store == null
                                ? Icons.add_business_outlined
                                : Icons.edit_outlined,
                          ),
                          label: Text(
                            store == null ? 'ساخت فروشگاه' : 'ویرایش فروشگاه',
                          ),
                        ),
                        if (store != null &&
                            (store.status == 'draft' ||
                                store.status == 'rejected')) ...[
                          SizedBox(height: r.v(12)),
                          OutlinedButton.icon(
                            onPressed: state.isSaving ? null : _submit,
                            icon: const Icon(Icons.send_outlined),
                            label: const Text('ارسال برای بررسی'),
                          ),
                        ],
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
