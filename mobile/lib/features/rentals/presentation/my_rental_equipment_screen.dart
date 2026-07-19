import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../state/rental_management_controller.dart';
import 'my_lessor_profile_screen.dart';

class MyRentalEquipmentScreen extends ConsumerStatefulWidget {
  const MyRentalEquipmentScreen({super.key});
  @override
  ConsumerState<MyRentalEquipmentScreen> createState() => _State();
}

class _State extends ConsumerState<MyRentalEquipmentScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(rentalManagementProvider.notifier).loadEquipment(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(rentalManagementProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('تجهیزات اجاره‌ای من'),
        actions: [
          IconButton(
            onPressed: () => context.push('/rentals/me/equipment/new'),
            icon: const Icon(Icons.add),
          ),
        ],
      ),
      body:
          s.isLoading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                onRefresh:
                    () =>
                        ref
                            .read(rentalManagementProvider.notifier)
                            .loadEquipment(),
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    if (s.errorMessage != null) Text(s.errorMessage!),
                    if (s.successMessage != null) Text(s.successMessage!),
                    if (s.equipment.isEmpty)
                      const SizedBox(
                        height: 300,
                        child: FarmEmptyView(
                          message: 'هنوز تجهیزی ثبت نشده است.',
                        ),
                      )
                    else
                      ...s.equipment.map(
                        (e) => Card(
                          child: ListTile(
                            onTap:
                                e.canEdit
                                    ? () => context.push(
                                      '/rentals/me/equipment/${e.id}/edit',
                                      extra: e,
                                    )
                                    : () => context.push(
                                      '/rentals/me/equipment/${e.id}/commercial',
                                    ),
                            title: Text(e.title),
                            subtitle: Text(rentalStatusLabel(e.status)),
                            trailing:
                                e.canSubmit
                                    ? IconButton(
                                      onPressed:
                                          () => ref
                                              .read(
                                                rentalManagementProvider
                                                    .notifier,
                                              )
                                              .submitEquipment(e.id),
                                      icon: const Icon(Icons.send_outlined),
                                    )
                                    : const Icon(Icons.chevron_left),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
    );
  }
}
