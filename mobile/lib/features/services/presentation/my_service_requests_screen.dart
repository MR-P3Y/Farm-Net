import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_request_controller.dart';

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
      appBar: AppBar(title: const Text('درخواست‌های خدمات من')),
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
                  const Padding(
                    padding: EdgeInsets.only(top: 100),
                    child: FarmEmptyView(
                      message: 'هنوز درخواست خدمتی ثبت نکرده‌اید.',
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
                            '${request.offerTitle ?? 'خدمت'} • ${_statusLabel(request.status)}',
                          ),
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
            title: const Text('لغو درخواست'),
            content: Text('درخواست «${request.title}» لغو شود؟'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('لغو'),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref
          .read(serviceRequestControllerProvider.notifier)
          .cancel(request.id, reason: 'لغو توسط کاربر از اپلیکیشن موبایل');
    }
  }
}

String _statusLabel(String status) =>
    const {
      'open': 'باز',
      'accepted': 'پذیرفته‌شده',
      'in_progress': 'در حال انجام',
      'completed': 'تکمیل‌شده',
      'cancelled': 'لغوشده',
      'rejected': 'ردشده',
    }[status] ??
    status;
