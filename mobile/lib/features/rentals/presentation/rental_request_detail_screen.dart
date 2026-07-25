import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/rental_models.dart';
import '../state/rental_request_controller.dart';
import '../../reviews/data/review_models.dart';

class RentalRequestDetailScreen extends ConsumerStatefulWidget {
  const RentalRequestDetailScreen({super.key, required this.requestId});
  final int requestId;
  @override
  ConsumerState<RentalRequestDetailScreen> createState() => _State();
}

class _State extends ConsumerState<RentalRequestDetailScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref
          .read(rentalRequestControllerProvider.notifier)
          .loadDetail(widget.requestId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rentalRequestControllerProvider);
    final row = state.selected?.id == widget.requestId ? state.selected : null;
    return Scaffold(
      appBar: AppBar(title: const Text('جزئیات درخواست اجاره')),
      body:
          state.isLoading
              ? const FarmLoadingView()
              : RefreshIndicator(
                onRefresh:
                    () => ref
                        .read(rentalRequestControllerProvider.notifier)
                        .loadDetail(widget.requestId),
                child: ListView(
                  padding: const EdgeInsets.all(16),
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
                      Text(state.successMessage!),
                    if (row == null)
                      const Center(
                        child: Padding(
                          padding: EdgeInsets.all(60),
                          child: Text('درخواست پیدا نشد.'),
                        ),
                      )
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
                                      row.equipmentTitle,
                                      style:
                                          Theme.of(
                                            context,
                                          ).textTheme.titleLarge,
                                    ),
                                  ),
                                  Chip(
                                    label: Text(
                                      rentalRequestStatusLabel(row.status),
                                    ),
                                  ),
                                ],
                              ),
                              const Divider(),
                              _Info('موجر', row.lessorDisplayName ?? '-'),
                              _Info('شروع', row.startsAt.format(context, showTime: true)),
                              _Info('پایان', row.endsAt.format(context, showTime: true)),
                              _Info('تعداد واحد', '${row.requestedUnits}'),
                              _Info(
                                'اپراتور',
                                row.operatorRequested
                                    ? 'درخواست شده'
                                    : 'بدون اپراتور',
                              ),
                              if (row.totalAmount != null)
                                _Info(
                                  'مبلغ کل',
                                  '${row.totalAmount!.toStringAsFixed(0)} ${row.currency == 'TOMAN' ? 'تومان' : row.currency}',
                                ),
                              if ((row.deliveryAddress ?? '').isNotEmpty)
                                _Info('نشانی تحویل', row.deliveryAddress!),
                              if ((row.requesterNote ?? '').isNotEmpty)
                                _Info('یادداشت من', row.requesterNote!),
                              if ((row.lessorNote ?? '').isNotEmpty)
                                _Info('یادداشت موجر', row.lessorNote!),
                              if ((row.cancelReason ?? '').isNotEmpty)
                                _Info('دلیل لغو', row.cancelReason!),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'تاریخچه وضعیت',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              if (row.statusLogs.isEmpty)
                                const Padding(
                                  padding: EdgeInsets.only(top: 12),
                                  child: Text('تاریخچه‌ای ثبت نشده است.'),
                                )
                              else
                                ...row.statusLogs.map(
                                  (log) => ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: const Icon(Icons.circle, size: 12),
                                    title: Text(
                                      rentalRequestStatusLabel(log.toStatus),
                                    ),
                                    subtitle: Text(
                                      [
                                        if (log.fromStatus != null)
                                          'از ${rentalRequestStatusLabel(log.fromStatus!)}',
                                        if ((log.note ?? '').isNotEmpty)
                                          log.note!,
                                      ].join(' • '),
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                      if (row.canCancel)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: OutlinedButton.icon(
                            onPressed:
                                state.isSaving ? null : () => _cancel(row),
                            icon: const Icon(Icons.cancel_outlined),
                            label: const Text('لغو درخواست'),
                          ),
                        ),
                      if (row.status == 'completed')
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: FilledButton.icon(
                            onPressed: () => context.push(
                              '/reviews/create',
                              extra: ReviewCreateTarget(
                                sourceType: 'rental_request',
                                sourceId: row.id,
                                subjectType: 'rental_equipment',
                                subjectId: row.equipmentId,
                                title: row.equipmentTitle,
                              ),
                            ),
                            icon: const Icon(Icons.rate_review_outlined),
                            label: const Text('ثبت نظر برای این تجهیز'),
                          ),
                        ),
                    ],
                  ],
                ),
              ),
    );
  }

  Future<void> _cancel(RentalRequest row) async {
    final reason = TextEditingController();
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('لغو درخواست'),
            content: TextField(
              controller: reason,
              decoration: const InputDecoration(
                labelText: 'دلیل لغو',
                hintText: 'حداقل دو حرف',
              ),
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
    if (yes == true && reason.text.trim().length >= 2) {
      await ref
          .read(rentalRequestControllerProvider.notifier)
          .cancel(row.id, reason.text.trim());
    }
    reason.dispose();
  }
}

class _Info extends StatelessWidget {
  const _Info(this.label, this.value);
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 5),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 110, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}
