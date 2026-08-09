import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/utils/dates.dart';
import '../data/rental_models.dart';
import '../data/rental_repository.dart';

class RentalCommercialScreen extends ConsumerStatefulWidget {
  const RentalCommercialScreen({super.key, required this.equipmentId});
  final int equipmentId;
  @override
  ConsumerState<RentalCommercialScreen> createState() => _State();
}

class _State extends ConsumerState<RentalCommercialScreen> {
  List<RentalPricingRule> _prices = [];
  List<RentalAvailabilityBlock> _blocks = [];
  bool _loading = true;
  String? _error;
  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final repo = ref.read(rentalRepositoryProvider);
      final values = await Future.wait([
        repo.ownerPricing(widget.equipmentId),
        repo.ownerAvailability(widget.equipmentId),
      ]);
      if (mounted) {
        setState(() {
          _prices = values[0] as List<RentalPricingRule>;
          _blocks = values[1] as List<RentalAvailabilityBlock>;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'دریافت قیمت و دسترس‌پذیری ناموفق بود.';
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('قیمت و دسترس‌پذیری')),
    body:
        _loading
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  if (_error != null)
                    Text(
                      _error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'تعرفه‌ها',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      IconButton(
                        onPressed: _addPrice,
                        icon: const Icon(Icons.add),
                      ),
                    ],
                  ),
                  if (_prices.isEmpty)
                    const Text('تعرفه‌ای ثبت نشده است.')
                  else
                    ..._prices.map(
                      (p) => ListTile(
                        title: Text(
                          '${p.priceAmount.toStringAsFixed(0)} ${p.currency == 'TOMAN' ? 'تومان' : p.currency} / ${rentalUnitLabel(p.unit)}',
                        ),
                        subtitle: Text(
                          'حداقل ${p.minimumUnits} • ${p.operatorIncluded ? 'با اپراتور' : 'بدون اپراتور'}',
                        ),
                        trailing: IconButton(
                          onPressed: () => _deletePrice(p),
                          icon: const Icon(Icons.delete_outline),
                        ),
                      ),
                    ),
                  const Divider(),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'بازه‌های مسدود',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      IconButton(
                        onPressed: _addBlock,
                        icon: const Icon(Icons.add),
                      ),
                    ],
                  ),
                  if (_blocks.isEmpty)
                    const Text('بازه مسدودی ثبت نشده است.')
                  else
                    ..._blocks.map(
                      (b) => ListTile(
                        onTap: () => _editBlock(b),
                        title: Text(_blockLabel(b.blockType)),
                        subtitle: Text(
                          '${b.startsAt.format(context)} تا ${b.endsAt.format(context)}',
                        ),
                        trailing: IconButton(
                          onPressed: () => _delete(b),
                          icon: const Icon(Icons.delete_outline),
                        ),
                      ),
                    ),
                ],
              ),
            ),
  );
  Future<void> _addPrice() async {
    final amount = TextEditingController(),
        minimum = TextEditingController(text: '1');
    String unit = 'day';
    bool operator = false;
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (c) => StatefulBuilder(
            builder:
                (c, set) => AlertDialog(
                  title: const Text('افزودن تعرفه'),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      DropdownButton<String>(
                        value: unit,
                        items:
                            ['hour', 'day', 'week', 'hectare', 'project']
                                .map(
                                  (u) => DropdownMenuItem(
                                    value: u,
                                    child: Text(rentalUnitLabel(u)),
                                  ),
                                )
                                .toList(),
                        onChanged: (v) => set(() => unit = v ?? unit),
                      ),
                      TextField(
                        controller: amount,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(labelText: 'مبلغ'),
                      ),
                      TextField(
                        controller: minimum,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'حداقل واحد',
                        ),
                      ),
                      SwitchListTile(
                        value: operator,
                        onChanged: (v) => set(() => operator = v),
                        title: const Text('همراه اپراتور'),
                      ),
                    ],
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(c, false),
                      child: const Text('انصراف'),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.pop(c, true),
                      child: const Text('ذخیره'),
                    ),
                  ],
                ),
          ),
    );
    if (yes == true) {
      final row = RentalPricingRule(
        id: 0,
        unit: unit,
        operatorIncluded: operator,
        priceAmount: double.tryParse(amount.text) ?? 0,
        minimumUnits: double.tryParse(minimum.text) ?? 1,
        currency: 'TOMAN',
      );
      try {
        await ref.read(rentalRepositoryProvider).replacePricing(
          widget.equipmentId,
          [..._prices, row],
        );
        await _load();
      } catch (_) {
        if (mounted) setState(() => _error = 'ذخیره تعرفه ناموفق بود.');
      }
    }
    amount.dispose();
    minimum.dispose();
  }

  Future<void> _addBlock() async {
    final start = await showLocalizedDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (start == null || !mounted) return;
    final end = await showLocalizedDatePicker(
      context: context,
      initialDate: start.add(const Duration(days: 1)),
      firstDate: start.add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (end == null) return;
    try {
      await ref
          .read(rentalRepositoryProvider)
          .createAvailability(
            widget.equipmentId,
            RentalAvailabilityBlock(
              id: 0,
              equipmentId: widget.equipmentId,
              blockType: 'unavailable',
              startsAt: start,
              endsAt: end,
            ),
          );
      await _load();
    } catch (_) {
      if (mounted) setState(() => _error = 'ثبت بازه ناموفق بود.');
    }
  }

  Future<void> _delete(RentalAvailabilityBlock b) async {
    await ref
        .read(rentalRepositoryProvider)
        .deleteAvailability(widget.equipmentId, b.id);
    await _load();
  }

  Future<void> _deletePrice(RentalPricingRule price) async {
    final remaining = _prices.where((item) => item.id != price.id).toList();
    if (remaining.isEmpty) {
      setState(() => _error = 'حداقل یک تعرفه باید باقی بماند.');
      return;
    }
    try {
      await ref
          .read(rentalRepositoryProvider)
          .replacePricing(widget.equipmentId, remaining);
      await _load();
    } catch (_) {
      if (mounted) setState(() => _error = 'حذف تعرفه ناموفق بود.');
    }
  }

  Future<void> _editBlock(RentalAvailabilityBlock block) async {
    final start = await showLocalizedDatePicker(
      context: context,
      initialDate: block.startsAt,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (start == null || !mounted) return;
    final end = await showLocalizedDatePicker(
      context: context,
      initialDate:
          block.endsAt.isAfter(start)
              ? block.endsAt
              : start.add(const Duration(days: 1)),
      firstDate: start.add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (end == null) return;
    try {
      await ref
          .read(rentalRepositoryProvider)
          .updateAvailability(
            widget.equipmentId,
            RentalAvailabilityBlock(
              id: block.id,
              equipmentId: block.equipmentId,
              blockType: block.blockType,
              startsAt: start,
              endsAt: end,
              note: block.note,
            ),
          );
      await _load();
    } catch (_) {
      if (mounted) setState(() => _error = 'ویرایش بازه ناموفق بود.');
    }
  }

  String _blockLabel(String v) =>
      const {
        'unavailable': 'غیردردسترس',
        'maintenance': 'تعمیرات',
        'owner_reserved': 'رزرو مالک',
      }[v] ??
      v;
}
