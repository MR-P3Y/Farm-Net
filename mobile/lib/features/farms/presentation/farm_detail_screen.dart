import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';
import '../../home/state/home_dashboard_controller.dart';

class FarmDetailScreen extends ConsumerStatefulWidget {
  const FarmDetailScreen({required this.farmId, this.farm, super.key});
  final int farmId;
  final FarmModel? farm;

  @override
  ConsumerState<FarmDetailScreen> createState() => _FarmDetailScreenState();
}

class _FarmDetailScreenState extends ConsumerState<FarmDetailScreen> {
  List<FarmPlotModel>? _plots;
  Object? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final rows = await ref.read(farmRepositoryProvider).plots(widget.farmId);
      if (mounted) {
        setState(() {
          _plots = rows;
          _error = null;
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _createPlot() async {
    final name = TextEditingController();
    final area = TextEditingController();
    final latitude = TextEditingController();
    final longitude = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('قطعه جدید'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: name,
                    decoration: const InputDecoration(labelText: 'نام *'),
                  ),
                  TextField(
                    controller: area,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'مساحت متر مربع *',
                    ),
                  ),
                  TextField(
                    controller: latitude,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    decoration: const InputDecoration(
                      labelText: 'عرض جغرافیایی',
                    ),
                  ),
                  TextField(
                    controller: longitude,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    decoration: const InputDecoration(
                      labelText: 'طول جغرافیایی',
                    ),
                  ),
                ],
              ),
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
    );
    if (accepted != true ||
        name.text.trim().isEmpty ||
        double.tryParse(area.text) == null) {
      return;
    }
    final lat = double.tryParse(latitude.text);
    final lon = double.tryParse(longitude.text);
    if ((lat == null) != (lon == null)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('عرض و طول جغرافیایی باید با هم وارد شوند'),
          ),
        );
      }
      return;
    }
    try {
      await ref.read(farmRepositoryProvider).createPlot(widget.farmId, {
        'name': name.text.trim(),
        'area_sqm': double.parse(area.text),
        'latitude': lat,
        'longitude': lon,
        'boundary': null,
      });
      await _load();
      await ref.read(homeDashboardControllerProvider.notifier).refresh();
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
    appBar: FarmAppBar(title: widget.farm?.name ?? 'جزئیات مزرعه'),
    floatingActionButton: FloatingActionButton.extended(
      onPressed: _createPlot,
      icon: const Icon(Icons.add_location_alt_outlined),
      label: const Text('قطعه جدید'),
    ),
    body:
        _error != null
            ? _ErrorState(error: _error!, onRetry: _load)
            : _plots == null
            ? const FarmLoadingView()
            : _plots!.isEmpty
            ? const FarmEmptyView(message: 'قطعه‌ای ثبت نشده است')
            : RefreshIndicator(
              onRefresh: _load,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _plots!.length,
                itemBuilder: (context, index) {
                  final plot = _plots![index];
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.landscape_outlined),
                      title: Text(plot.name),
                      subtitle: Text(
                        '${plot.areaSqm} متر مربع${plot.latitude == null ? ' • بدون موقعیت دقیق' : ' • دارای موقعیت'}',
                      ),
                      trailing: const Icon(Icons.chevron_left),
                      onTap:
                          () => context.push(
                            '/farms/${widget.farmId}/plots/${plot.id}',
                            extra: plot,
                          ),
                    ),
                  );
                },
              ),
            ),
  );
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(error.toString(), textAlign: TextAlign.center),
        TextButton(onPressed: onRetry, child: const Text('تلاش دوباره')),
      ],
    ),
  );
}
