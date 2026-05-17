import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../state/store_controller.dart';

class PublicStoreDetailScreen extends ConsumerStatefulWidget {
  const PublicStoreDetailScreen({required this.slug, super.key});

  final String slug;

  @override
  ConsumerState<PublicStoreDetailScreen> createState() =>
      _PublicStoreDetailScreenState();
}

class _PublicStoreDetailScreenState
    extends ConsumerState<PublicStoreDetailScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref
          .read(storeControllerProvider.notifier)
          .loadPublicStoreDetail(widget.slug);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(storeControllerProvider);
    final store = state.selectedPublicStore;

    return Scaffold(
      appBar: AppBar(
        title: Text(store?.name ?? 'جزئیات فروشگاه'),
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

          if (state.errorMessage != null) {
            return Center(child: Text(state.errorMessage!));
          }

          if (store == null) {
            return const Center(child: Text('فروشگاه پیدا نشد.'));
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
                        const Icon(Icons.storefront_outlined, size: 56),
                        SizedBox(height: r.v(12)),
                        Text(
                          store.name,
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        SizedBox(height: r.v(8)),
                        Text(
                          store.description ?? 'توضیحی ثبت نشده است.',
                          textAlign: TextAlign.center,
                        ),
                        const Divider(height: 32),
                        _InfoRow(label: 'نوع فروشگاه', value: store.storeType),
                        _InfoRow(label: 'تلفن', value: store.phone ?? '-'),
                        _InfoRow(label: 'ایمیل', value: store.email ?? '-'),
                        _InfoRow(label: 'آدرس', value: store.address ?? '-'),
                        _InfoRow(
                          label: 'کد پستی',
                          value: store.postalCode ?? '-',
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
