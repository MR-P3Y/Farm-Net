import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/rental_models.dart';
import '../state/rental_management_controller.dart';

class RentalWorkbenchDetailScreen extends ConsumerStatefulWidget {
  const RentalWorkbenchDetailScreen({super.key, required this.requestId});
  final int requestId;
  @override
  ConsumerState<RentalWorkbenchDetailScreen> createState() => _State();
}

class _State extends ConsumerState<RentalWorkbenchDetailScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref
          .read(rentalWorkbenchProvider.notifier)
          .loadDetail(widget.requestId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rentalWorkbenchProvider);
    final request =
        state.selected?.id == widget.requestId ? state.selected : null;
    return Scaffold(
      appBar: AppBar(title: const Text('جزئیات درخواست موجر')),
      body:
          state.isLoading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                onRefresh:
                    () => ref
                        .read(rentalWorkbenchProvider.notifier)
                        .loadDetail(widget.requestId),
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: [
                    if (state.isSaving) const LinearProgressIndicator(),
                    if (state.errorMessage != null) Text(state.errorMessage!),
                    if (state.successMessage != null)
                      Text(state.successMessage!),
                    if (request == null)
                      const Center(child: Text('درخواست پیدا نشد.'))
                    else ...[
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      request.equipmentTitle,
                                      style:
                                          Theme.of(
                                            context,
                                          ).textTheme.titleLarge,
                                    ),
                                  ),
                                  Chip(
                                    label: Text(
                                      rentalRequestStatusLabel(request.status),
                                    ),
                                  ),
                                ],
                              ),
                              const Divider(),
                              Text(
                                'بازه: ${_date(request.startsAt)} تا ${_date(request.endsAt)}',
                              ),
                              Text('واحد: ${request.requestedUnits}'),
                              if ((request.deliveryAddress ?? '').isNotEmpty)
                                Text('نشانی: ${request.deliveryAddress}'),
                              if ((request.requesterNote ?? '').isNotEmpty)
                                Text('یادداشت: ${request.requesterNote}'),
                            ],
                          ),
                        ),
                      ),
                      Card(
                        child: Column(
                          children:
                              request.statusLogs
                                  .map(
                                    (log) => ListTile(
                                      leading: const Icon(
                                        Icons.circle,
                                        size: 12,
                                      ),
                                      title: Text(
                                        rentalRequestStatusLabel(log.toStatus),
                                      ),
                                      subtitle: Text(log.note ?? ''),
                                    ),
                                  )
                                  .toList(),
                        ),
                      ),
                      ...request.lessorNextStatuses.map(
                        (status) => Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: FilledButton(
                            onPressed:
                                state.isSaving
                                    ? null
                                    : () => _update(request, status),
                            child: Text(_action(status)),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
    );
  }

  Future<void> _update(RentalRequest request, String status) async {
    final note = TextEditingController();
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(_action(status)),
            content: TextField(
              controller: note,
              decoration: const InputDecoration(labelText: 'یادداشت — اختیاری'),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('تأیید'),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref
          .read(rentalWorkbenchProvider.notifier)
          .update(request.id, status, note: note.text);
    }
    note.dispose();
  }

  String _date(DateTime value) => '${value.year}/${value.month}/${value.day}';
  String _action(String status) =>
      const {
        'accepted': 'پذیرش درخواست',
        'rejected': 'رد درخواست',
        'in_progress': 'شروع اجاره',
        'completed': 'تکمیل اجاره',
      }[status] ??
      status;
}
