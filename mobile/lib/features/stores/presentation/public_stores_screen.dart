import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/store_models.dart';
import '../state/store_controller.dart';

class PublicStoresScreen extends ConsumerStatefulWidget {
  const PublicStoresScreen({super.key});

  @override
  ConsumerState<PublicStoresScreen> createState() => _PublicStoresScreenState();
}

class _PublicStoresScreenState extends ConsumerState<PublicStoresScreen> {
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
      ref.read(storeControllerProvider.notifier).loadPublicStores();
    });
  }

  Future<void> _search() async {
    await ref
        .read(storeControllerProvider.notifier)
        .loadPublicStores(q: _searchController.text.trim());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(storeControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('فروشگاه‌ها'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return RefreshIndicator(
            onRefresh: () {
              return ref
                  .read(storeControllerProvider.notifier)
                  .loadPublicStores();
            },
            child: ListView(
              padding: r.pagePadding(),
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _searchController,
                        decoration: const InputDecoration(
                          labelText: 'جستجوی فروشگاه',
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
                else if (state.publicStores.isEmpty)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(24),
                      child: Text('فروشگاهی برای نمایش وجود ندارد.'),
                    ),
                  )
                else
                  ...state.publicStores.map(
                    (store) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: _StoreCard(store: store),
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

class _StoreCard extends StatelessWidget {
  const _StoreCard({required this.store});

  final Store store;

  String _typeLabel(String type) {
    switch (type) {
      case 'agriculture_inputs':
        return 'نهاده‌های کشاورزی';
      case 'equipment':
        return 'تجهیزات';
      case 'seeds':
        return 'بذر';
      case 'fertilizer':
        return 'کود';
      case 'pesticide':
        return 'سموم';
      case 'mixed':
        return 'چندمنظوره';
      case 'other':
        return 'سایر';
      default:
        return type;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.storefront_outlined),
        title: Text(store.name),
        subtitle: Text(
          '${_typeLabel(store.storeType)}\n${store.address ?? '-'}',
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          context.push('/stores/${store.slug}');
        },
      ),
    );
  }
}
