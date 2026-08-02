import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../home/state/home_dashboard_controller.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';
import 'create_plot_screen.dart';
import 'farm_profile_editor_screen.dart';
import 'widgets/farm_profile_action_dialogs.dart';
import 'widgets/farm_plots_map.dart';

class FarmDetailScreen extends ConsumerStatefulWidget {
  const FarmDetailScreen({required this.farmId, this.farm, super.key});
  final int farmId;
  final FarmModel? farm;

  @override
  ConsumerState<FarmDetailScreen> createState() => _FarmDetailScreenState();
}

class _FarmDetailScreenState extends ConsumerState<FarmDetailScreen> {
  FarmModel? _farm;
  List<FarmPlotModel>? _plots;
  Object? _error;
  _FarmDetailView _view = _FarmDetailView.list;
  bool _mutating = false;

  @override
  void initState() {
    super.initState();
    _farm = widget.farm;
    _load();
  }

  Future<void> _load() async {
    try {
      final repository = ref.read(farmRepositoryProvider);
      final farm = await repository.farm(widget.farmId);
      final rows = await repository.plots(widget.farmId);
      if (mounted) {
        setState(() {
          _farm = farm;
          _plots = rows;
          _error = null;
        });
      }
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _createPlot() async {
    LatLng? initialCenter;
    for (final plot in _plots ?? const <FarmPlotModel>[]) {
      if (plot.hasLocation) {
        initialCenter = LatLng(plot.latitude!, plot.longitude!);
        break;
      }
    }
    final created = await Navigator.of(context).push<FarmPlotModel>(
      MaterialPageRoute(
        builder:
            (_) => CreatePlotScreen(
              farmId: widget.farmId,
              farmName: _farm?.name ?? context.l10n.tr(fa: 'مزرعه', en: 'Farm'),
              initialCenter: initialCenter,
            ),
      ),
    );
    if (created != null) {
      await _load();
      await ref.read(homeDashboardControllerProvider.notifier).refresh();
    }
  }

  void _openPlot(FarmPlotModel plot) =>
      context.push('/farms/${widget.farmId}/plots/${plot.id}', extra: plot);

  Future<void> _editFarm() async {
    final farm = _farm;
    if (farm == null || !farm.canEdit || _mutating) return;
    final updated = await Navigator.of(context).push<FarmModel>(
      MaterialPageRoute(builder: (_) => FarmProfileEditorScreen(farm: farm)),
    );
    if (updated == null || !mounted) return;
    setState(() => _farm = updated);
    await ref.read(homeDashboardControllerProvider.notifier).refresh();
  }

  Future<void> _archiveFarm() async {
    final farm = _farm;
    if (farm == null || !farm.canArchive || _mutating) return;
    final request = await showFarmArchiveDialog(context, farm);
    if (request == null || !mounted) return;
    setState(() => _mutating = true);
    try {
      await ref
          .read(farmRepositoryProvider)
          .archiveFarm(farm.id, reason: request.reason);
      await ref.read(homeDashboardControllerProvider.notifier).refresh();
      if (mounted) Navigator.of(context).pop(true);
    } catch (error) {
      if (!mounted) return;
      setState(() => _mutating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'حذف مزرعه انجام نشد: $error',
              en: 'Could not remove the Farm: $error',
            ),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: FarmAppBar(
        title: _farm?.name ?? l10n.tr(fa: 'جزئیات مزرعه', en: 'Farm details'),
        actions: [
          IconButton(
            tooltip: l10n.tr(fa: 'جعبه‌ابزار مزرعه', en: 'Farm toolbox'),
            onPressed:
                _farm == null
                    ? null
                    : () => context.push('/toolbox', extra: _farm),
            icon: const Icon(Icons.handyman_outlined),
          ),
          IconButton(
            tooltip: l10n.tr(fa: 'تازه‌سازی', en: 'Refresh'),
            onPressed: _mutating ? null : _load,
            icon: const Icon(Icons.refresh_rounded),
          ),
          if (_farm?.canEdit ?? false)
            IconButton(
              tooltip: l10n.tr(fa: 'ویرایش مزرعه', en: 'Edit farm'),
              onPressed: _mutating ? null : _editFarm,
              icon: const Icon(Icons.edit_outlined),
            ),
          if (_farm?.canArchive ?? false)
            IconButton(
              tooltip: l10n.tr(fa: 'حذف مزرعه', en: 'Remove farm'),
              onPressed: _mutating ? null : _archiveFarm,
              icon:
                  _mutating
                      ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : const Icon(Icons.delete_outline_rounded),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: (_farm?.canEdit ?? false) && !_mutating ? _createPlot : null,
        icon: const Icon(Icons.add_location_alt_outlined),
        label: Text(l10n.tr(fa: 'قطعه جدید', en: 'Add Plot')),
      ),
      body:
          _error != null
              ? _ErrorState(error: _error!, onRetry: _load)
              : _plots == null
              ? const FarmLoadingView()
              : _plots!.isEmpty
              ? FarmEmptyView(
                message: l10n.tr(
                  fa: 'قطعه‌ای ثبت نشده است',
                  en: 'No Plot has been added',
                ),
              )
              : Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                    child: SizedBox(
                      width: double.infinity,
                      child: SegmentedButton<_FarmDetailView>(
                        segments: [
                          ButtonSegment(
                            value: _FarmDetailView.list,
                            icon: const Icon(Icons.view_list_rounded),
                            label: Text(l10n.tr(fa: 'فهرست', en: 'List')),
                          ),
                          ButtonSegment(
                            value: _FarmDetailView.map,
                            icon: const Icon(Icons.map_rounded),
                            label: Text(l10n.tr(fa: 'نقشه', en: 'Map')),
                          ),
                        ],
                        selected: {_view},
                        onSelectionChanged:
                            (value) => setState(() => _view = value.first),
                      ),
                    ),
                  ),
                  Expanded(
                    child:
                        _view == _FarmDetailView.map
                            ? Padding(
                              padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
                              child: FarmPlotsMap(
                                plots: _plots!,
                                onPlotTap: _openPlot,
                              ),
                            )
                            : RefreshIndicator(
                              onRefresh: _load,
                              child: ListView.builder(
                                padding: const EdgeInsets.all(16),
                                itemCount: _plots!.length,
                                itemBuilder: (context, index) {
                                  final plot = _plots![index];
                                  return Card(
                                    child: ListTile(
                                      leading: CircleAvatar(
                                        child: Icon(
                                          plot.hasBoundary
                                              ? Icons.polyline_rounded
                                              : plot.hasLocation
                                              ? Icons.location_on_outlined
                                              : Icons.landscape_outlined,
                                        ),
                                      ),
                                      title: Text(plot.name),
                                      subtitle: Text(
                                        '${_formatArea(context, plot.areaSqm)} • ${plot.hasBoundary
                                            ? l10n.tr(fa: 'مرز ثبت‌شده', en: 'Boundary saved')
                                            : plot.hasLocation
                                            ? l10n.tr(fa: 'موقعیت ثبت‌شده', en: 'Location saved')
                                            : l10n.tr(fa: 'بدون موقعیت', en: 'No location')}',
                                      ),
                                      trailing: const Icon(Icons.chevron_left),
                                      onTap: () => _openPlot(plot),
                                    ),
                                  );
                                },
                              ),
                            ),
                  ),
                ],
              ),
    );
  }

  static String _formatArea(BuildContext context, double area) {
    final l10n = context.l10n;
    final raw =
        area >= 10000
            ? (area / 10000).toStringAsFixed(2)
            : area.toStringAsFixed(0);
    final number = l10n.isFa ? toPersianDigits(raw) : raw;
    return area >= 10000
        ? l10n.tr(fa: '$number هکتار', en: '$number ha')
        : l10n.tr(fa: '$number متر مربع', en: '$number m²');
  }
}

enum _FarmDetailView { list, map }

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
        TextButton(onPressed: onRetry, child: Text(context.l10n.retry)),
      ],
    ),
  );
}
