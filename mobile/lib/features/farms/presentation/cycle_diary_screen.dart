import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';

class CycleDiaryScreen extends ConsumerStatefulWidget {
  const CycleDiaryScreen({
    required this.farmId,
    required this.plotId,
    required this.cycleId,
    this.cycle,
    super.key,
  });
  final int farmId;
  final int plotId;
  final int cycleId;
  final CropCycleModel? cycle;

  @override
  ConsumerState<CycleDiaryScreen> createState() => _CycleDiaryScreenState();
}

class _CycleDiaryScreenState extends ConsumerState<CycleDiaryScreen> {
  List<FarmOperationModel>? _operations;
  List<FarmHarvestModel>? _harvests;
  late String _status;
  Object? _error;

  bool get _active => _status == 'active';

  @override
  void initState() {
    super.initState();
    _status = widget.cycle?.status ?? 'planned';
    _load();
  }

  Future<void> _load() async {
    try {
      final repository = ref.read(farmRepositoryProvider);
      final values = await Future.wait([
        repository.operations(widget.farmId, widget.plotId, widget.cycleId),
        repository.harvests(widget.farmId, widget.plotId, widget.cycleId),
      ]);
      if (mounted) {
        setState(() {
          _operations = values[0] as List<FarmOperationModel>;
          _harvests = values[1] as List<FarmHarvestModel>;
          _error = null;
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _transition(String action) async {
    try {
      final value = await ref
          .read(farmRepositoryProvider)
          .transition(widget.farmId, widget.plotId, widget.cycleId, action);
      if (mounted) setState(() => _status = value.status);
    } catch (error) {
      _message(error);
    }
  }

  Future<void> _addOperation() async {
    final title = TextEditingController();
    String type = 'monitoring';
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: const Text('ثبت عملیات'),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      DropdownButtonFormField<String>(
                        initialValue: type,
                        items: const [
                          DropdownMenuItem(
                            value: 'monitoring',
                            child: Text('بازدید و پایش'),
                          ),
                          DropdownMenuItem(
                            value: 'irrigation',
                            child: Text('آبیاری'),
                          ),
                          DropdownMenuItem(
                            value: 'fertilizing',
                            child: Text('کوددهی'),
                          ),
                          DropdownMenuItem(
                            value: 'spraying',
                            child: Text('سم‌پاشی'),
                          ),
                          DropdownMenuItem(
                            value: 'weeding',
                            child: Text('وجین'),
                          ),
                          DropdownMenuItem(value: 'other', child: Text('سایر')),
                        ],
                        onChanged:
                            (value) =>
                                setDialogState(() => type = value ?? type),
                      ),
                      TextField(
                        controller: title,
                        decoration: const InputDecoration(labelText: 'عنوان *'),
                      ),
                    ],
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('انصراف'),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('ثبت'),
                    ),
                  ],
                ),
          ),
    );
    if (accepted != true || title.text.trim().isEmpty) return;
    try {
      await ref.read(farmRepositoryProvider).createOperation(
        widget.farmId,
        widget.plotId,
        widget.cycleId,
        {
          'operation_type': type,
          'title': title.text.trim(),
          'occurred_on': _today(),
        },
      );
      await _load();
    } catch (error) {
      _message(error);
    }
  }

  Future<void> _addHarvest() async {
    final units = await ref.read(farmRepositoryProvider).harvestUnits();
    if (!mounted || units.isEmpty) return;
    final quantity = TextEditingController();
    MeasurementUnitModel unit = units.first;
    final grade = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: const Text('ثبت برداشت'),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextField(
                        controller: quantity,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(labelText: 'مقدار *'),
                      ),
                      DropdownButtonFormField<MeasurementUnitModel>(
                        initialValue: unit,
                        decoration: const InputDecoration(
                          labelText: 'واحد برداشت',
                        ),
                        items:
                            units
                                .map(
                                  (item) => DropdownMenuItem(
                                    value: item,
                                    child: Text(
                                      '${item.title} (${item.symbol})',
                                    ),
                                  ),
                                )
                                .toList(),
                        onChanged:
                            (value) =>
                                setDialogState(() => unit = value ?? unit),
                      ),
                      TextField(
                        controller: grade,
                        decoration: const InputDecoration(
                          labelText: 'درجه کیفیت',
                        ),
                      ),
                    ],
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('انصراف'),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: const Text('ثبت'),
                    ),
                  ],
                ),
          ),
    );
    if (accepted != true) return;
    try {
      await ref.read(farmRepositoryProvider).createHarvest(
        widget.farmId,
        widget.plotId,
        widget.cycleId,
        {
          'harvested_on': _today(),
          'quantity': double.parse(quantity.text),
          'measurement_unit_id': unit.id,
          'quality_grade': grade.text.trim().isEmpty ? null : grade.text.trim(),
        },
      );
      await _load();
    } catch (error) {
      _message(error);
    }
  }

  void _message(Object error) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: FarmAppBar(title: widget.cycle?.title ?? 'دفتر چرخه کشت'),
    body:
        _operations == null && _error == null
            ? const FarmLoadingView()
            : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Chip(label: Text('وضعیت: $_status')),
                          if (_status == 'planned')
                            FilledButton.icon(
                              onPressed: () => _transition('start'),
                              icon: const Icon(Icons.play_arrow),
                              label: const Text('شروع چرخه'),
                            ),
                          if (_active)
                            FilledButton.icon(
                              onPressed: () => _transition('complete'),
                              icon: const Icon(Icons.check),
                              label: const Text('تکمیل چرخه'),
                            ),
                          if (_status == 'planned' || _active)
                            TextButton(
                              onPressed: () => _transition('cancel'),
                              child: const Text('لغو چرخه'),
                            ),
                        ],
                      ),
                    ),
                  ),
                  if (_error != null) Text(_error.toString()),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'عملیات',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      if (_active)
                        IconButton(
                          onPressed: _addOperation,
                          icon: const Icon(Icons.add),
                        ),
                    ],
                  ),
                  if (_operations?.isEmpty ?? true)
                    const Text('عملیاتی ثبت نشده است'),
                  ...?_operations?.map(
                    (item) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.task_alt_outlined),
                        title: Text(item.title),
                        subtitle: Text(
                          '${item.type} • ${item.occurredOn.toLocal().toString().split(' ').first}',
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'برداشت‌ها',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      if (_active)
                        IconButton(
                          onPressed: _addHarvest,
                          icon: const Icon(Icons.add),
                        ),
                    ],
                  ),
                  if (_harvests?.isEmpty ?? true)
                    const Text('برداشتی ثبت نشده است'),
                  ...?_harvests?.map(
                    (item) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.inventory_2_outlined),
                        title: Text('${item.quantity} ${item.unitSymbol}'),
                        subtitle: Text(item.qualityGrade ?? 'بدون درجه کیفیت'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
  );
}

String _today() {
  final now = DateTime.now();
  return '${now.year.toString().padLeft(4, '0')}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
}
