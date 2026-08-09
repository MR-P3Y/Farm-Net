import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';

class PlotDetailScreen extends ConsumerStatefulWidget {
  const PlotDetailScreen({
    required this.farmId,
    required this.plotId,
    this.plot,
    super.key,
  });
  final int farmId;
  final int plotId;
  final FarmPlotModel? plot;

  @override
  ConsumerState<PlotDetailScreen> createState() => _PlotDetailScreenState();
}

class _PlotDetailScreenState extends ConsumerState<PlotDetailScreen> {
  List<CropCycleModel>? _cycles;
  FarmWeatherModel? _weather;
  Object? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repository = ref.read(farmRepositoryProvider);
      final cycles = await repository.cycles(widget.farmId, widget.plotId);
      FarmWeatherModel? weather;
      if (widget.plot?.latitude != null) {
        try {
          weather = await repository.weather(widget.farmId, widget.plotId);
        } catch (_) {
          weather = null;
        }
      }
      if (mounted) {
        setState(() {
          _cycles = cycles;
          _weather = weather;
          _error = null;
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _refreshWeather() async {
    try {
      final value = await ref
          .read(farmRepositoryProvider)
          .weather(widget.farmId, widget.plotId, refresh: true);
      if (mounted) setState(() => _weather = value);
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    }
  }

  Future<void> _createCycle() async {
    final repository = ref.read(farmRepositoryProvider);
    final crops = await repository.crops();
    if (!mounted) return;
    if (crops.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('فهرست محصول در دسترس نیست')),
      );
      return;
    }
    CropReference selected = crops.first;
    final title = TextEditingController();
    DateTime starts = DateTime.now();
    DateTime ends = starts.add(const Duration(days: 120));
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: const Text('چرخه کشت جدید'),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      DropdownButtonFormField<CropReference>(
                        initialValue: selected,
                        decoration: const InputDecoration(labelText: 'محصول'),
                        items:
                            crops
                                .map(
                                  (crop) => DropdownMenuItem(
                                    value: crop,
                                    child: Text(crop.title),
                                  ),
                                )
                                .toList(),
                        onChanged:
                            (value) => setDialogState(
                              () => selected = value ?? selected,
                            ),
                      ),
                      TextField(
                        controller: title,
                        decoration: const InputDecoration(
                          labelText: 'عنوان اختیاری',
                        ),
                      ),
                      ListTile(
                        title: const Text('شروع برنامه‌ریزی‌شده'),
                        subtitle: Text(starts.format(context)),
                        onTap: () async {
                          final value = await showLocalizedDatePicker(
                            context: context,
                            firstDate: DateTime(2020),
                            lastDate: DateTime(2040),
                            initialDate: starts,
                          );
                          if (value != null) {
                            setDialogState(() => starts = value);
                          }
                        },
                      ),
                      ListTile(
                        title: const Text('پایان برنامه‌ریزی‌شده'),
                        subtitle: Text(ends.format(context)),
                        onTap: () async {
                          final value = await showLocalizedDatePicker(
                            context: context,
                            firstDate: starts,
                            lastDate: DateTime(2040),
                            initialDate: ends.isBefore(starts) ? starts : ends,
                          );
                          if (value != null) {
                            setDialogState(() => ends = value);
                          }
                        },
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
      await repository.createCycle(widget.farmId, widget.plotId, {
        'crop_id': selected.id,
        'title': title.text.trim().isEmpty ? null : title.text.trim(),
        'cultivation_mode': 'single',
        'planned_start_date': _date(starts),
        'planned_end_date': _date(ends),
      });
      await _load();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(error.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: FarmAppBar(title: widget.plot?.name ?? 'قطعه کشاورزی'),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: _createCycle,
      icon: const Icon(Icons.eco_outlined),
      label: const Text('چرخه جدید'),
    ),
    body:
        _cycles == null && _error == null
            ? const FarmLoadingView()
            : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_error != null)
                    Card(
                      color: Theme.of(context).colorScheme.errorContainer,
                      child: ListTile(
                        title: Text(_error.toString()),
                        trailing: IconButton(
                          onPressed: _load,
                          icon: const Icon(Icons.refresh),
                        ),
                      ),
                    ),
                  _WeatherCard(
                    hasCoordinates: widget.plot?.latitude != null,
                    weather: _weather,
                    onRefresh: _refreshWeather,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'چرخه‌های کشت',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  if (_cycles?.isEmpty ?? true)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Text(
                          'هنوز چرخه کشتی ثبت نشده است',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ...?_cycles?.map(
                    (cycle) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.grass_outlined),
                        title: Text(
                          cycle.title ?? 'چرخه محصول ${cycle.cropId}',
                        ),
                        subtitle: Text(
                          '${_status(cycle.status)} • ${cycle.plannedStartDate.format(context)} تا ${cycle.plannedEndDate.format(context)}',
                        ),
                        trailing: const Icon(Icons.chevron_left),
                        onTap:
                            () => context.push(
                              '/farms/${widget.farmId}/plots/${widget.plotId}/cycles/${cycle.id}',
                              extra: cycle,
                            ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
  );
}

class _WeatherCard extends StatelessWidget {
  const _WeatherCard({
    required this.hasCoordinates,
    required this.weather,
    required this.onRefresh,
  });
  final bool hasCoordinates;
  final FarmWeatherModel? weather;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          const Icon(Icons.cloud_outlined, size: 36),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'آب‌وهوای این قطعه',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  !hasCoordinates
                      ? 'برای آب‌وهوا، موقعیت دقیق قطعه را ثبت کنید'
                      : weather == null
                      ? 'اطلاعاتی دریافت نشده'
                      : '${weather!.temperatureC ?? '-'}°C • ${weather!.conditionText ?? 'نامشخص'} • ${weather!.alerts.length} هشدار',
                ),
              ],
            ),
          ),
          if (hasCoordinates)
            IconButton(onPressed: onRefresh, icon: const Icon(Icons.refresh)),
        ],
      ),
    ),
  );
}

String _date(DateTime date) =>
    '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

String _status(String value) => switch (value) {
  'planned' => 'برنامه‌ریزی‌شده',
  'active' => 'فعال',
  'completed' => 'تکمیل‌شده',
  'cancelled' => 'لغوشده',
  _ => value,
};
