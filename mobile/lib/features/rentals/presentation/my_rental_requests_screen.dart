import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/rental_models.dart';
import '../state/rental_request_controller.dart';

class MyRentalRequestsScreen extends ConsumerStatefulWidget {
  const MyRentalRequestsScreen({super.key});
  @override
  ConsumerState<MyRentalRequestsScreen> createState() => _State();
}

class _State extends ConsumerState<MyRentalRequestsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(rentalRequestControllerProvider.notifier).loadList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rentalRequestControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('درخواست‌های اجاره من')),
      body:
          state.isLoading
              ? const FarmLoadingView()
              : RefreshIndicator(
                onRefresh:
                    () =>
                        ref
                            .read(rentalRequestControllerProvider.notifier)
                            .loadList(),
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    if (state.errorMessage != null)
                      Text(
                        state.errorMessage!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    if (state.requests.isEmpty)
                      const SizedBox(
                        height: 300,
                        child: FarmEmptyView(
                          message: 'هنوز درخواست اجاره‌ای ثبت نکرده‌اید.',
                        ),
                      )
                    else
                      ...state.requests.map(
                        (r) => Card(
                          child: ListTile(
                            onTap:
                                () => context.push('/rentals/requests/${r.id}'),
                            title: Text(r.equipmentTitle),
                            subtitle: Text(
                              '${rentalRequestStatusLabel(r.status)} • ${_date(r.startsAt)} تا ${_date(r.endsAt)}',
                            ),
                            trailing: const Icon(Icons.chevron_left),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
    );
  }

  String _date(DateTime value) => '${value.year}/${value.month}/${value.day}';
}
