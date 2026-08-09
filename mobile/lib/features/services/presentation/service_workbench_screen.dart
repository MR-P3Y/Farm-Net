import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../state/service_workbench_controller.dart';
import 'service_ui.dart';

class ServiceWorkbenchScreen extends ConsumerStatefulWidget {
  const ServiceWorkbenchScreen({super.key});
  @override
  ConsumerState<ServiceWorkbenchScreen> createState() => _State();
}

class _State extends ConsumerState<ServiceWorkbenchScreen> {
  bool _loaded = false;
  String? _status;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(serviceWorkbenchProvider.notifier).loadList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(serviceWorkbenchProvider);
    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'میزکار خدمات‌دهنده',
          en: 'Service provider workbench',
        ),
        fallbackLocation: '/activity',
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (s.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (s.isProviderUnapproved) {
            return _Denied(
              onRetry:
                  () => ref
                      .read(serviceWorkbenchProvider.notifier)
                      .loadList(status: _status),
            );
          }
          return RefreshIndicator(
            onRefresh:
                () => ref
                    .read(serviceWorkbenchProvider.notifier)
                    .loadList(status: _status),
            child: ListView(
              padding: r.pagePadding(),
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                DropdownButtonFormField<String?>(
                  initialValue: _status,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'فیلتر وضعیت',
                      en: 'Status filter',
                    ),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: null,
                      child: Text(
                        context.l10n.tr(fa: 'همه وضعیت‌ها', en: 'All statuses'),
                      ),
                    ),
                    ...[
                      'open',
                      'accepted',
                      'in_progress',
                      'completed',
                      'rejected',
                      'cancelled',
                    ].map(
                      (v) => DropdownMenuItem(
                        value: v,
                        child: Text(serviceRequestStatusLabel(context, v)),
                      ),
                    ),
                  ],
                  onChanged: (v) {
                    setState(() => _status = v);
                    ref
                        .read(serviceWorkbenchProvider.notifier)
                        .loadList(status: v);
                  },
                ),
                const SizedBox(height: 12),
                if (s.errorMessage != null)
                  Text(
                    s.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (s.requests.isEmpty)
                  Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(
                      message: context.l10n.tr(
                        fa: 'درخواست واگذارشده‌ای وجود ندارد.',
                        en: 'There are no assigned requests.',
                      ),
                    ),
                  )
                else
                  ...s.requests.map(
                    (q) => Card(
                      child: ListTile(
                        onTap:
                            () => context.push(
                              '/services/workbench/requests/${q.id}',
                            ),
                        title: Text(q.title),
                        subtitle: Text(
                          '${q.offerTitle ?? context.l10n.tr(fa: 'خدمت', en: 'Service')} • ${q.categoryTitle ?? '-'}\n${context.l10n.tr(fa: 'درخواست‌دهنده', en: 'Requester')} #${q.requesterUserId ?? '-'}',
                        ),
                        isThreeLine: true,
                        trailing: Chip(
                          label: Text(
                            serviceRequestStatusLabel(context, q.status),
                          ),
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
}

class _Denied extends StatelessWidget {
  const _Denied({required this.onRetry});
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.lock_outline, size: 48),
          const SizedBox(height: 12),
          Text(
            context.l10n.tr(
              fa:
                  'برای استفاده از میزکار، پروفایل خدمات‌دهنده شما باید تأیید شده باشد.',
              en:
                  'Your service provider profile must be approved to use the workbench.',
            ),
            textAlign: TextAlign.center,
          ),
          TextButton(onPressed: onRetry, child: Text(context.l10n.retry)),
        ],
      ),
    ),
  );
}
