import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../data/service_models.dart';
import '../state/service_workbench_controller.dart';

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
      appBar: AppBar(title: const Text('میزکار خدمات‌دهنده')),
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
                  decoration: const InputDecoration(
                    labelText: 'فیلتر وضعیت',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    const DropdownMenuItem(
                      value: null,
                      child: Text('همه وضعیت‌ها'),
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
                        child: Text(requestStatusLabel(v)),
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
                  const Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(
                      message: 'درخواست واگذارشده‌ای وجود ندارد.',
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
                          '${q.offerTitle ?? 'خدمت'} • ${q.categoryTitle ?? '-'}\nدرخواست‌دهنده #${q.requesterUserId ?? '-'}',
                        ),
                        isThreeLine: true,
                        trailing: Chip(label: Text(q.statusLabelFa)),
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
          const Text(
            'برای استفاده از میزکار، پروفایل خدمات‌دهنده شما باید تأیید شده باشد.',
            textAlign: TextAlign.center,
          ),
          TextButton(onPressed: onRetry, child: const Text('تلاش دوباره')),
        ],
      ),
    ),
  );
}
