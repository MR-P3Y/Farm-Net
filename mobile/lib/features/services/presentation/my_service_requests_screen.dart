import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_request_controller.dart';
import 'service_ui.dart';

class MyServiceRequestsScreen extends ConsumerStatefulWidget {
  const MyServiceRequestsScreen({super.key});
  @override
  ConsumerState<MyServiceRequestsScreen> createState() =>
      _MyServiceRequestsScreenState();
}

class _MyServiceRequestsScreenState
    extends ConsumerState<MyServiceRequestsScreen> {
  bool _loaded = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(serviceRequestControllerProvider.notifier).loadList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceRequestControllerProvider);
    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'درخواست‌های خدمات من',
          en: 'My service requests',
        ),
        fallbackLocation: '/services',
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) return const FarmLoadingView();
          return RefreshIndicator(
            onRefresh:
                () =>
                    ref
                        .read(serviceRequestControllerProvider.notifier)
                        .loadList(),
            child: ListView(
              padding: r.pagePadding(),
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                if (state.isSaving) const LinearProgressIndicator(),
                if (state.errorMessage != null)
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (state.successMessage != null)
                  Text(
                    state.successMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                if (state.requests.isEmpty)
                  Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(
                      message: context.l10n.tr(
                        fa: 'هنوز درخواست خدمتی ثبت نکرده‌اید.',
                        en: 'You have not submitted a service request yet.',
                      ),
                    ),
                  )
                else
                  ...state.requests.map(
                    (request) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(10)),
                      child: Card(
                        child: ListTile(
                          onTap:
                              () => context.push(
                                '/services/requests/${request.id}',
                              ),
                          title: Text(request.title),
                          subtitle: Text(
                            '${request.offerTitle ?? context.l10n.tr(fa: 'خدمت', en: 'Service')} • ${serviceRequestStatusLabel(context, request.status)}\n${formatApiDate(context, request.createdAt, showTime: true)}',
                          ),
                          isThreeLine: true,
                          trailing:
                              request.canCancel
                                  ? IconButton(
                                    icon: const Icon(Icons.cancel_outlined),
                                    onPressed: () => _cancel(request),
                                  )
                                  : const Icon(Icons.chevron_left),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _cancel(ServiceRequest request) async {
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              context.l10n.tr(fa: 'لغو درخواست', en: 'Cancel request'),
            ),
            content: Text(
              context.l10n.tr(
                fa: 'درخواست «${request.title}» لغو شود؟',
                en: 'Cancel “${request.title}”?',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Back')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(context.l10n.tr(fa: 'لغو', en: 'Cancel request')),
              ),
            ],
          ),
    );
    if (yes == true) {
      if (!mounted) return;
      await ref
          .read(serviceRequestControllerProvider.notifier)
          .cancel(
            request.id,
            reason: context.l10n.tr(
              fa: 'لغو توسط کاربر از اپلیکیشن موبایل',
              en: 'Cancelled by the user from the mobile app',
            ),
          );
    }
  }
}
