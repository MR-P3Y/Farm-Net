import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../state/service_management_controller.dart';

class MyOffersScreen extends ConsumerStatefulWidget {
  const MyOffersScreen({super.key});
  @override
  ConsumerState<MyOffersScreen> createState() => _State();
}

class _State extends ConsumerState<MyOffersScreen> {
  bool _loaded = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(serviceManagementProvider.notifier).loadOffers(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(serviceManagementProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('خدمات من')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/services/me/offers/new'),
        icon: const Icon(Icons.add),
        label: const Text('خدمت جدید'),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (s.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return RefreshIndicator(
            onRefresh:
                () => ref.read(serviceManagementProvider.notifier).loadOffers(),
            child: ListView(
              padding: r.pagePadding(),
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                if (s.errorMessage != null)
                  Text(
                    s.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (s.successMessage != null)
                  Text(
                    s.successMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                if (s.offers.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(message: 'هنوز خدمتی ثبت نکرده‌اید.'),
                  )
                else
                  ...s.offers.map(
                    (o) => Card(
                      child: ListTile(
                        title: Text(o.title),
                        subtitle: Text(
                          '${o.statusLabelFa} • ${o.category?.title ?? '-'} • ${_price(o)}',
                        ),
                        leading:
                            o.primaryMedia == null
                                ? const Icon(Icons.agriculture_outlined)
                                : const Icon(Icons.image_outlined),
                        onTap:
                            o.canEdit
                                ? () => context.push(
                                  '/services/me/offers/${o.id}/edit',
                                  extra: o,
                                )
                                : null,
                        trailing:
                            o.canSubmit
                                ? IconButton(
                                  icon: const Icon(Icons.send_outlined),
                                  onPressed:
                                      s.isSaving ? null : () => _submit(o.id),
                                )
                                : const Icon(Icons.chevron_left),
                      ),
                    ),
                  ),
                const SizedBox(height: 80),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _submit(int id) async {
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (c) => AlertDialog(
            title: const Text('ارسال خدمت'),
            content: const Text('این خدمت برای بررسی ارسال شود؟'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: const Text('ارسال'),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref.read(serviceManagementProvider.notifier).submitOffer(id);
    }
  }

  String _price(dynamic o) =>
      o.priceAmount == null
          ? 'توافقی'
          : '${o.priceAmount!.toStringAsFixed(0)} ${o.currency == 'TOMAN' ? 'تومان' : o.currency}';
}
