import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../data/rental_models.dart';
import '../state/rental_management_controller.dart';

class RentalWorkbenchScreen extends ConsumerStatefulWidget {
  const RentalWorkbenchScreen({super.key});
  @override
  ConsumerState<RentalWorkbenchScreen> createState() => _State();
}

class _State extends ConsumerState<RentalWorkbenchScreen> {
  String? _status;
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(rentalWorkbenchProvider.notifier).loadList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rentalWorkbenchProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('میزکار موجر')),
      body:
          state.isLoading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                onRefresh:
                    () => ref
                        .read(rentalWorkbenchProvider.notifier)
                        .loadList(status: _status),
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    DropdownButtonFormField<String?>(
                      initialValue: _status,
                      decoration: const InputDecoration(labelText: 'وضعیت'),
                      items: [
                        const DropdownMenuItem(value: null, child: Text('همه')),
                        ...[
                          'pending',
                          'accepted',
                          'in_progress',
                          'completed',
                          'rejected',
                          'cancelled',
                        ].map(
                          (value) => DropdownMenuItem(
                            value: value,
                            child: Text(rentalRequestStatusLabel(value)),
                          ),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() => _status = value);
                        ref
                            .read(rentalWorkbenchProvider.notifier)
                            .loadList(status: value);
                      },
                    ),
                    if (state.errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(state.errorMessage!),
                      ),
                    if (state.requests.isEmpty)
                      const SizedBox(
                        height: 300,
                        child: FarmEmptyView(
                          message: 'درخواست واگذارشده‌ای وجود ندارد.',
                        ),
                      )
                    else
                      ...state.requests.map(
                        (request) => Card(
                          child: ListTile(
                            onTap:
                                () => context.push(
                                  '/rentals/workbench/requests/${request.id}',
                                ),
                            title: Text(request.equipmentTitle),
                            subtitle: Text('درخواست #${request.id}'),
                            trailing: Chip(
                              label: Text(
                                rentalRequestStatusLabel(request.status),
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
    );
  }
}
