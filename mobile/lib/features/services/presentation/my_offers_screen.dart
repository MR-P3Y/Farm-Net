import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../data/service_models.dart';
import '../state/service_management_controller.dart';
import 'service_ui.dart';

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
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'خدمات من', en: 'My services'),
        fallbackLocation: '/activity',
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/services/me/offers/new'),
        icon: const Icon(Icons.add),
        label: Text(context.l10n.tr(fa: 'خدمت جدید', en: 'New service')),
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
                  Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(
                      message: context.l10n.tr(
                        fa: 'هنوز خدمتی ثبت نکرده‌اید.',
                        en: 'You have not created a service yet.',
                      ),
                    ),
                  )
                else
                  ...s.offers.map(
                    (o) => Card(
                      child: ListTile(
                        title: Text(o.title),
                        subtitle: Text(
                          '${serviceOfferStatusLabel(context, o.status)} • ${o.category?.title ?? '-'} • ${_price(context, o)}',
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
            title: Text(
              context.l10n.tr(fa: 'ارسال خدمت', en: 'Submit service'),
            ),
            content: Text(
              context.l10n.tr(
                fa: 'این خدمت برای بررسی ارسال شود؟',
                en: 'Submit this service for review?',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: Text(context.l10n.tr(fa: 'ارسال', en: 'Submit')),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref.read(serviceManagementProvider.notifier).submitOffer(id);
    }
  }

  String _price(BuildContext context, ServiceOfferOwner o) =>
      o.priceAmount == null
          ? context.l10n.tr(fa: 'توافقی', en: 'Negotiable')
          : o.currency == 'TOMAN'
          ? formatToman(context, o.priceAmount!)
          : '${o.priceAmount!.toStringAsFixed(0)} ${o.currency}';
}
