import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/rental_models.dart';
import '../state/rental_discovery_controller.dart';
import '../state/rental_request_controller.dart';

class RentalRequestCreateScreen extends ConsumerStatefulWidget {
  const RentalRequestCreateScreen({super.key, required this.equipmentId});
  final int equipmentId;
  @override
  ConsumerState<RentalRequestCreateScreen> createState() => _State();
}

class _State extends ConsumerState<RentalRequestCreateScreen> {
  final _units = TextEditingController();
  final _address = TextEditingController();
  final _note = TextEditingController();
  int? _pricingId;
  DateTime? _start;
  DateTime? _end;
  bool _available = false;
  @override
  void dispose() {
    _units.dispose();
    _address.dispose();
    _note.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final detail = ref.watch(rentalEquipmentDetailProvider(widget.equipmentId));
    final request = ref.watch(rentalRequestControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('درخواست اجاره')),
      body: detail.when(
        loading: () => const FarmLoadingView(),
        error:
            (_, _) =>
                const Center(child: Text('دریافت اطلاعات تجهیز ناموفق بود.')),
        data:
            (data) => ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Card(
                  child: ListTile(
                    title: Text(data.equipment.title),
                    subtitle: Text(
                      data.equipment.lessorDisplayName ?? 'موجر تأییدشده',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<int>(
                  initialValue: _pricingId,
                  decoration: const InputDecoration(
                    labelText: 'تعرفه اجاره',
                    border: OutlineInputBorder(),
                  ),
                  items:
                      data.pricing
                          .map(
                            (p) => DropdownMenuItem(
                              value: p.id,
                              child: Text(
                                '${p.priceAmount.toStringAsFixed(0)} ${p.currency == 'TOMAN' ? 'تومان' : p.currency} / ${rentalUnitLabel(p.unit)}',
                              ),
                            ),
                          )
                          .toList(),
                  onChanged:
                      (v) => setState(() {
                        _pricingId = v;
                        _available = false;
                      }),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _units,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'تعداد واحد اجاره',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _pick(true),
                        icon: const Icon(Icons.event),
                        label: Text(
                          _start == null
                              ? 'زمان شروع'
                              : _start!.format(context, showTime: true),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _pick(false),
                        icon: const Icon(Icons.event_available),
                        label: Text(
                          _end == null
                              ? 'زمان پایان'
                              : _end!.format(context, showTime: true),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _address,
                  minLines: 2,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    labelText: 'نشانی تحویل — اختیاری',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _note,
                  minLines: 2,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    labelText: 'یادداشت برای موجر — اختیاری',
                    border: OutlineInputBorder(),
                  ),
                ),
                if (request.errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Text(
                      request.errorMessage!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ),
                if (request.successMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Text(request.successMessage!),
                  ),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: request.isSaving ? null : _check,
                  icon: const Icon(Icons.fact_check_outlined),
                  label: const Text('بررسی دسترس‌پذیری'),
                ),
                const SizedBox(height: 8),
                FilledButton.icon(
                  onPressed:
                      request.isSaving || !_available
                          ? null
                          : () => _submit(data),
                  icon: const Icon(Icons.send_outlined),
                  label: const Text('ثبت درخواست اجاره'),
                ),
              ],
            ),
      ),
    );
  }

  Future<void> _pick(bool start) async {
    final date = await showLocalizedDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (date == null || !mounted) return;
    final time = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 8, minute: 0),
    );
    if (time != null) {
      setState(() {
        final value = DateTime(
          date.year,
          date.month,
          date.day,
          time.hour,
          time.minute,
        );
        if (start) {
          _start = value;
        } else {
          _end = value;
        }
        _available = false;
      });
    }
  }

  Future<void> _check() async {
    if (_start == null || _end == null || !_end!.isAfter(_start!)) {
      _message('بازه شروع و پایان معتبر انتخاب کنید.');
      return;
    }
    final ok = await ref
        .read(rentalRequestControllerProvider.notifier)
        .checkAvailability(widget.equipmentId, _start!, _end!);
    if (mounted) setState(() => _available = ok);
  }

  Future<void> _submit(RentalEquipmentDetail detail) async {
    final price = detail.pricing.where((p) => p.id == _pricingId).firstOrNull;
    final units = double.tryParse(_units.text.trim());
    if (price == null ||
        units == null ||
        units < price.minimumUnits ||
        _start == null ||
        _end == null) {
      _message('تعرفه و تعداد واحد معتبر را کامل کنید.');
      return;
    }
    final row = await ref
        .read(rentalRequestControllerProvider.notifier)
        .create(
          RentalRequestInput(
            equipmentId: widget.equipmentId,
            pricingRuleId: price.id,
            startsAt: _start!,
            endsAt: _end!,
            requestedUnits: units,
            operatorRequested: price.operatorIncluded,
            deliveryAddress: _address.text,
            requesterNote: _note.text,
          ),
        );
    if (row != null && mounted) context.go('/rentals/requests/${row.id}');
  }

  void _message(String value) => ScaffoldMessenger.of(
    context,
  ).showSnackBar(SnackBar(content: Text(value)));
}
