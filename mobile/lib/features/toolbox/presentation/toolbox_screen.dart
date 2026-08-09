import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../farms/data/farm_models.dart';
import '../../farms/data/farm_repository.dart';
import '../data/toolbox_api.dart';
import '../data/toolbox_models.dart';
import '../data/toolbox_repository.dart';
import '../domain/farm_calculators.dart';
import '../domain/toolbox_number_input.dart';
import 'calculator_screen.dart';
import 'toolbox_context.dart';
import 'toolbox_localization.dart';

class ToolboxScreen extends ConsumerStatefulWidget {
  const ToolboxScreen({this.initialFarm, super.key});

  final FarmModel? initialFarm;

  @override
  ConsumerState<ToolboxScreen> createState() => _ToolboxScreenState();
}

class _ToolboxScreenState extends ConsumerState<ToolboxScreen> {
  List<FarmModel> _farms = const [];
  List<FarmPlotModel> _plots = const [];
  List<CropCycleModel> _cycles = const [];
  FarmModel? _farm;
  FarmPlotModel? _plot;
  CropCycleModel? _cycle;
  List<FarmToolCalculationModel> _calculations = const [];
  List<FarmFinancialEntryModel> _costs = const [];
  List<FarmPlanModel> _plans = const [];
  FarmFinancialSummaryModel? _summary;
  bool _loadingContext = true;
  bool _loadingData = false;
  Object? _contextError;
  Object? _remoteError;
  int _loadGeneration = 0;

  ToolboxContextSelection? get _selection =>
      _farm == null
          ? null
          : ToolboxContextSelection(farm: _farm!, plot: _plot, cycle: _cycle);

  @override
  void initState() {
    super.initState();
    _loadContext();
  }

  Future<void> _loadContext() async {
    setState(() {
      _loadingContext = true;
      _contextError = null;
    });
    try {
      final farms = await ref.read(farmRepositoryProvider).farms();
      FarmModel? selected;
      if (farms.isNotEmpty) {
        selected = farms.firstWhere(
          (item) => item.id == widget.initialFarm?.id,
          orElse: () => farms.first,
        );
      }
      final plots =
          selected == null
              ? const <FarmPlotModel>[]
              : await ref.read(farmRepositoryProvider).plots(selected.id);
      if (!mounted) return;
      setState(() {
        _farms = farms;
        _farm = selected;
        _plots = plots;
        _plot = null;
        _cycle = null;
        _cycles = const [];
        _loadingContext = false;
      });
      await _reloadRemote();
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loadingContext = false;
        _contextError = error;
      });
    }
  }

  Future<void> _selectFarm(int? farmId) async {
    final farm = _farms.where((item) => item.id == farmId).firstOrNull;
    setState(() {
      _farm = farm;
      _plot = null;
      _cycle = null;
      _plots = const [];
      _cycles = const [];
    });
    if (farm != null) {
      try {
        final plots = await ref.read(farmRepositoryProvider).plots(farm.id);
        if (!mounted || _farm?.id != farm.id) return;
        setState(() => _plots = plots);
      } catch (error) {
        if (mounted) setState(() => _remoteError = error);
      }
    }
    await _reloadRemote();
  }

  Future<void> _selectPlot(int plotId) async {
    final plot =
        plotId == 0
            ? null
            : _plots.where((item) => item.id == plotId).firstOrNull;
    setState(() {
      _plot = plot;
      _cycle = null;
      _cycles = const [];
    });
    final farm = _farm;
    if (plot != null && farm != null) {
      try {
        final cycles = await ref
            .read(farmRepositoryProvider)
            .cycles(farm.id, plot.id);
        if (!mounted || _plot?.id != plot.id) return;
        setState(
          () =>
              _cycles = cycles
                  .where((item) => item.status != 'cancelled')
                  .toList(growable: false),
        );
      } catch (error) {
        if (mounted) setState(() => _remoteError = error);
      }
    }
    await _reloadRemote();
  }

  Future<void> _selectCycle(int cycleId) async {
    setState(
      () =>
          _cycle =
              cycleId == 0
                  ? null
                  : _cycles.where((item) => item.id == cycleId).firstOrNull,
    );
    await _reloadRemote();
  }

  Future<void> _reloadRemote() async {
    final selection = _selection;
    final generation = ++_loadGeneration;
    if (selection == null) {
      if (mounted) {
        setState(() {
          _calculations = const [];
          _costs = const [];
          _plans = const [];
          _summary = null;
          _remoteError = null;
          _loadingData = false;
        });
      }
      return;
    }
    setState(() {
      _loadingData = true;
      _remoteError = null;
    });
    try {
      final repository = ref.read(toolboxRepositoryProvider);
      final results = await Future.wait<Object>([
        repository.calculations(
          farmId: selection.farmId,
          plotId: selection.plotId,
          cycleId: selection.cycleId,
        ),
        repository.costs(
          farmId: selection.farmId,
          plotId: selection.plotId,
          cycleId: selection.cycleId,
        ),
        repository.plans(
          farmId: selection.farmId,
          plotId: selection.plotId,
          cycleId: selection.cycleId,
        ),
        repository.costSummary(
          farmId: selection.farmId,
          plotId: selection.plotId,
          cycleId: selection.cycleId,
        ),
      ]);
      if (!mounted || generation != _loadGeneration) return;
      setState(() {
        _calculations = results[0] as List<FarmToolCalculationModel>;
        _costs = results[1] as List<FarmFinancialEntryModel>;
        _plans = results[2] as List<FarmPlanModel>;
        _summary = results[3] as FarmFinancialSummaryModel;
        _loadingData = false;
      });
    } catch (error) {
      if (!mounted || generation != _loadGeneration) return;
      setState(() {
        _remoteError = error;
        _loadingData = false;
      });
    }
  }

  Future<void> _openCalculator(FarmCalculatorType type) async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder:
            (_) => FarmCalculatorScreen(
              type: type,
              contextSelection: _selection,
              initialTotalCost:
                  type == FarmCalculatorType.costProfit
                      ? _summary?.expenseToman
                      : null,
            ),
      ),
    );
    if (saved == true) await _reloadRemote();
  }

  Future<void> _addCost() async {
    final selection = _selection;
    if (selection == null) return;
    final payload = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => _CostEntrySheet(selection: selection),
    );
    if (payload == null) return;
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .createCost(farmId: selection.farmId, payload: payload);
      await _reloadRemote();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _voidCost(FarmFinancialEntryModel entry) async {
    final controller = TextEditingController();
    final reason = await showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(
              context.l10n.tr(fa: 'ابطال ثبت مالی', en: 'Void entry'),
            ),
            content: TextField(
              controller: controller,
              autofocus: true,
              maxLength: 500,
              decoration: InputDecoration(
                labelText: context.l10n.tr(fa: 'دلیل ابطال', en: 'Void reason'),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () {
                  final value = controller.text.trim();
                  if (value.isNotEmpty) Navigator.pop(context, value);
                },
                child: Text(context.l10n.tr(fa: 'ابطال', en: 'Void')),
              ),
            ],
          ),
    );
    controller.dispose();
    if (reason == null || _farm == null) return;
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .voidCost(farmId: _farm!.id, entryId: entry.id, reason: reason);
      await _reloadRemote();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _addPlan() async {
    final selection = _selection;
    if (selection == null) return;
    final payload = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => _PlanEntrySheet(selection: selection),
    );
    if (payload == null) return;
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .createPlan(farmId: selection.farmId, payload: payload);
      await _reloadRemote();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _completePlan(FarmPlanModel plan) async {
    final canWriteToDiary = _cycles.any(
      (cycle) => cycle.id == plan.cycleId && cycle.status == 'active',
    );
    var writeToDiary = canWriteToDiary;
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => StatefulBuilder(
            builder:
                (context, setDialogState) => AlertDialog(
                  title: Text(
                    context.l10n.tr(
                      fa: 'تکمیل عملیات',
                      en: 'Complete operation',
                    ),
                  ),
                  content: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(plan.title),
                      CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        value: writeToDiary,
                        onChanged:
                            !canWriteToDiary
                                ? null
                                : (value) => setDialogState(
                                  () => writeToDiary = value ?? false,
                                ),
                        title: Text(
                          context.l10n.tr(
                            fa: 'هم‌زمان در دفتر عملیات چرخه ثبت شود',
                            en: 'Also write to the cycle operation diary',
                          ),
                        ),
                      ),
                    ],
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.pop(context, true),
                      child: Text(
                        context.l10n.tr(fa: 'انجام شد', en: 'Complete'),
                      ),
                    ),
                  ],
                ),
          ),
    );
    if (confirmed != true || _farm == null) return;
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .completePlan(
            farmId: _farm!.id,
            planId: plan.id,
            writeToDiary: writeToDiary,
          );
      await _reloadRemote();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _cancelPlan(FarmPlanModel plan) async {
    final controller = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(context.l10n.tr(fa: 'لغو برنامه', en: 'Cancel plan')),
            content: TextField(
              controller: controller,
              maxLength: 500,
              decoration: InputDecoration(
                labelText: context.l10n.tr(
                  fa: 'دلیل (اختیاری)',
                  en: 'Reason (optional)',
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text(context.l10n.tr(fa: 'بازگشت', en: 'Back')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, controller.text.trim()),
                child: Text(
                  context.l10n.tr(fa: 'لغو برنامه', en: 'Cancel plan'),
                ),
              ),
            ],
          ),
    );
    controller.dispose();
    if (result == null || _farm == null) return;
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .cancelPlan(
            farmId: _farm!.id,
            planId: plan.id,
            reason: result.isEmpty ? null : result,
          );
      await _reloadRemote();
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(localizeToolboxError(context, error))),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: FarmAppBar(
          title: context.l10n.tr(fa: 'جعبه‌ابزار مزرعه', en: 'Farm toolbox'),
          actions: [
            IconButton(
              tooltip: context.l10n.tr(fa: 'تازه‌سازی', en: 'Refresh'),
              onPressed: _loadingData ? null : _reloadRemote,
              icon: const Icon(Icons.refresh_rounded),
            ),
          ],
        ),
        body:
            _loadingContext
                ? const FarmLoadingView()
                : _contextError != null
                ? FarmEmptyView(
                  icon: Icons.cloud_off_rounded,
                  title: context.l10n.tr(
                    fa: 'مزارع دریافت نشدند',
                    en: 'Could not load farms',
                  ),
                  message: context.l10n.tr(
                    fa: 'ارتباط با سرور را بررسی و دوباره تلاش کنید.',
                    en: 'Check the server connection and try again.',
                  ),
                  actionLabel: context.l10n.retry,
                  onAction: _loadContext,
                )
                : Column(
                  children: [
                    _ContextCard(
                      farms: _farms,
                      plots: _plots,
                      cycles: _cycles,
                      farm: _farm,
                      plot: _plot,
                      cycle: _cycle,
                      onFarmChanged: _selectFarm,
                      onPlotChanged: _selectPlot,
                      onCycleChanged: _selectCycle,
                    ),
                    TabBar(
                      isScrollable: true,
                      tabs: [
                        Tab(
                          icon: const Icon(Icons.calculate_outlined),
                          text: context.l10n.tr(
                            fa: 'محاسبات',
                            en: 'Calculators',
                          ),
                        ),
                        Tab(
                          icon: const Icon(
                            Icons.account_balance_wallet_outlined,
                          ),
                          text: context.l10n.tr(fa: 'مالی', en: 'Finance'),
                        ),
                        Tab(
                          icon: const Icon(Icons.event_note_outlined),
                          text: context.l10n.tr(fa: 'تقویم کار', en: 'Plan'),
                        ),
                        Tab(
                          icon: const Icon(Icons.menu_book_outlined),
                          text: context.l10n.tr(fa: 'دفترچه', en: 'Notebook'),
                        ),
                      ],
                    ),
                    if (_remoteError != null)
                      _SyncNotice(error: _remoteError!, onRetry: _reloadRemote),
                    if (_loadingData) const LinearProgressIndicator(),
                    Expanded(
                      child: TabBarView(
                        children: [
                          _CalculatorGrid(onOpen: _openCalculator),
                          _FinanceTab(
                            selection: _selection,
                            summary: _summary,
                            entries: _costs,
                            onAdd: _addCost,
                            onVoid: _voidCost,
                            onOpenProfit:
                                () => _openCalculator(
                                  FarmCalculatorType.costProfit,
                                ),
                          ),
                          _PlanTab(
                            selection: _selection,
                            plans: _plans,
                            onAdd: _addPlan,
                            onComplete: _completePlan,
                            onCancel: _cancelPlan,
                          ),
                          _NotebookTab(
                            selection: _selection,
                            calculations: _calculations,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
      ),
    );
  }
}

class _SyncNotice extends StatelessWidget {
  const _SyncNotice({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final isOffline =
        error is ToolboxApiException &&
        (error as ToolboxApiException).isOffline;
    return Container(
      margin: const EdgeInsets.fromLTRB(8, 4, 8, 0),
      padding: const EdgeInsetsDirectional.only(start: 10),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(
            isOffline ? Icons.cloud_off_outlined : Icons.sync_problem_rounded,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              localizeToolboxError(context, error),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          TextButton(onPressed: onRetry, child: Text(context.l10n.retry)),
        ],
      ),
    );
  }
}

class _ContextCard extends StatelessWidget {
  const _ContextCard({
    required this.farms,
    required this.plots,
    required this.cycles,
    required this.farm,
    required this.plot,
    required this.cycle,
    required this.onFarmChanged,
    required this.onPlotChanged,
    required this.onCycleChanged,
  });

  final List<FarmModel> farms;
  final List<FarmPlotModel> plots;
  final List<CropCycleModel> cycles;
  final FarmModel? farm;
  final FarmPlotModel? plot;
  final CropCycleModel? cycle;
  final ValueChanged<int?> onFarmChanged;
  final ValueChanged<int> onPlotChanged;
  final ValueChanged<int> onCycleChanged;

  @override
  Widget build(BuildContext context) {
    final farmLabel =
        farm?.name ?? context.l10n.tr(fa: 'بدون مزرعه', en: 'No farm selected');
    final plotLabel =
        plot?.name ?? context.l10n.tr(fa: 'کل مزرعه', en: 'Whole farm');
    final cycleLabel =
        cycle == null
            ? null
            : cycle!.title ??
                context.l10n.tr(
                  fa: 'چرخه ${cycle!.id}',
                  en: 'Cycle ${cycle!.id}',
                );
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 6, 8, 2),
      child: FarmGlassCard(
        padding: EdgeInsets.zero,
        child: ExpansionTile(
          leading: const Icon(Icons.agriculture_outlined),
          title: Text(
            farmLabel,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          subtitle: Text(
            cycleLabel == null ? plotLabel : '$plotLabel • $cycleLabel',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          tilePadding: const EdgeInsetsDirectional.fromSTEB(12, 0, 8, 0),
          childrenPadding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
          children: [
            LayoutBuilder(
              builder: (context, constraints) {
                final width =
                    constraints.maxWidth >= 720
                        ? (constraints.maxWidth - 24) / 3
                        : constraints.maxWidth;
                return Wrap(
                  spacing: 12,
                  runSpacing: 10,
                  children: [
                    SizedBox(
                      width: width,
                      child: DropdownButtonFormField<int>(
                        key: ValueKey('toolbox-farm-${farm?.id}'),
                        initialValue: farm?.id,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(fa: 'مزرعه', en: 'Farm'),
                        ),
                        items:
                            farms
                                .map(
                                  (item) => DropdownMenuItem(
                                    value: item.id,
                                    child: Text(
                                      item.name,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                )
                                .toList(),
                        onChanged: onFarmChanged,
                      ),
                    ),
                    SizedBox(
                      width: width,
                      child: DropdownButtonFormField<int>(
                        key: ValueKey('toolbox-plot-${farm?.id}-${plot?.id}'),
                        initialValue: plot?.id ?? 0,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'قطعه (اختیاری)',
                            en: 'Plot (optional)',
                          ),
                        ),
                        items: [
                          DropdownMenuItem(
                            value: 0,
                            child: Text(
                              context.l10n.tr(fa: 'کل مزرعه', en: 'Whole farm'),
                            ),
                          ),
                          ...plots.map(
                            (item) => DropdownMenuItem(
                              value: item.id,
                              child: Text(
                                item.name,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                        ],
                        onChanged:
                            farm == null
                                ? null
                                : (value) => onPlotChanged(value ?? 0),
                      ),
                    ),
                    SizedBox(
                      width: width,
                      child: DropdownButtonFormField<int>(
                        key: ValueKey('toolbox-cycle-${plot?.id}-${cycle?.id}'),
                        initialValue: cycle?.id ?? 0,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'چرخه کشت (اختیاری)',
                            en: 'Crop cycle (optional)',
                          ),
                        ),
                        items: [
                          DropdownMenuItem(
                            value: 0,
                            child: Text(
                              context.l10n.tr(
                                fa: 'همه چرخه‌ها',
                                en: 'All cycles',
                              ),
                            ),
                          ),
                          ...cycles.map(
                            (item) => DropdownMenuItem(
                              value: item.id,
                              child: Text(
                                item.title ??
                                    context.l10n.tr(
                                      fa: 'چرخه ${item.id}',
                                      en: 'Cycle ${item.id}',
                                    ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                        ],
                        onChanged:
                            plot == null
                                ? null
                                : (value) => onCycleChanged(value ?? 0),
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _CalculatorGrid extends StatelessWidget {
  const _CalculatorGrid({required this.onOpen});
  final ValueChanged<FarmCalculatorType> onOpen;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final columns =
          constraints.maxWidth >= 1000
              ? 4
              : constraints.maxWidth >= 650
              ? 3
              : 2;
      return GridView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: FarmCalculatorType.values.length,
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: columns,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: columns == 2 ? 1.03 : 1.25,
        ),
        itemBuilder: (context, index) {
          final type = FarmCalculatorType.values[index];
          final definition = calculatorDefinition(type);
          return InkWell(
            borderRadius: BorderRadius.circular(20),
            onTap: () => onOpen(type),
            child: FarmGlassCard(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(child: Icon(definition.icon)),
                  const Spacer(),
                  Text(
                    definition.title(context),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    definition.description(context),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          );
        },
      );
    },
  );
}

class _FinanceTab extends StatelessWidget {
  const _FinanceTab({
    required this.selection,
    required this.summary,
    required this.entries,
    required this.onAdd,
    required this.onVoid,
    required this.onOpenProfit,
  });
  final ToolboxContextSelection? selection;
  final FarmFinancialSummaryModel? summary;
  final List<FarmFinancialEntryModel> entries;
  final VoidCallback onAdd;
  final ValueChanged<FarmFinancialEntryModel> onVoid;
  final VoidCallback onOpenProfit;

  @override
  Widget build(BuildContext context) {
    if (selection == null) {
      return FarmEmptyView(
        icon: Icons.agriculture_outlined,
        message: context.l10n.tr(
          fa: 'برای ثبت و مشاهده مالی، یک مزرعه انتخاب کنید.',
          en: 'Select a farm to manage finances.',
        ),
      );
    }
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        if (summary != null)
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _SummaryChip(
                label: context.l10n.tr(fa: 'هزینه', en: 'Expense'),
                value: formatToman(context, summary!.expenseToman),
                icon: Icons.trending_down_rounded,
              ),
              _SummaryChip(
                label: context.l10n.tr(fa: 'درآمد', en: 'Revenue'),
                value: formatToman(context, summary!.revenueToman),
                icon: Icons.trending_up_rounded,
              ),
              _SummaryChip(
                label: context.l10n.tr(fa: 'خالص', en: 'Net'),
                value: formatToman(context, summary!.netToman),
                icon: Icons.balance_rounded,
              ),
            ],
          ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: FilledButton.icon(
                onPressed: onAdd,
                icon: const Icon(Icons.add_rounded),
                label: Text(
                  context.l10n.tr(fa: 'ثبت هزینه/درآمد', en: 'Add entry'),
                ),
              ),
            ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: onOpenProfit,
              icon: const Icon(Icons.calculate_outlined),
              label: Text(context.l10n.tr(fa: 'سود', en: 'Profit')),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (entries.isEmpty)
          FarmEmptyView(
            icon: Icons.receipt_long_outlined,
            message: context.l10n.tr(
              fa: 'هنوز هزینه یا درآمدی ثبت نشده است.',
              en: 'No financial entries yet.',
            ),
          )
        else
          ...entries.map(
            (entry) => Card(
              child: ListTile(
                leading: CircleAvatar(
                  child: Icon(
                    entry.isExpense ? Icons.remove_rounded : Icons.add_rounded,
                  ),
                ),
                title: Text(_financialCategory(context, entry.category)),
                subtitle: Text(
                  '${formatDate(context, entry.occurredOn)}${entry.description == null ? '' : ' • ${entry.description}'}',
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '${entry.isExpense ? '−' : '+'}${formatToman(context, entry.amountToman)}',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    PopupMenuButton<String>(
                      onSelected: (_) => onVoid(entry),
                      itemBuilder:
                          (context) => [
                            PopupMenuItem(
                              value: 'void',
                              child: Text(
                                context.l10n.tr(
                                  fa: 'ابطال ثبت',
                                  en: 'Void entry',
                                ),
                              ),
                            ),
                          ],
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _SummaryChip extends StatelessWidget {
  const _SummaryChip({
    required this.label,
    required this.value,
    required this.icon,
  });
  final String label;
  final String value;
  final IconData icon;
  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minWidth: 150),
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      borderRadius: BorderRadius.circular(16),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w800)),
          ],
        ),
      ],
    ),
  );
}

class _PlanTab extends StatelessWidget {
  const _PlanTab({
    required this.selection,
    required this.plans,
    required this.onAdd,
    required this.onComplete,
    required this.onCancel,
  });
  final ToolboxContextSelection? selection;
  final List<FarmPlanModel> plans;
  final VoidCallback onAdd;
  final ValueChanged<FarmPlanModel> onComplete;
  final ValueChanged<FarmPlanModel> onCancel;

  @override
  Widget build(BuildContext context) {
    if (selection == null) {
      return FarmEmptyView(
        icon: Icons.event_note_outlined,
        message: context.l10n.tr(
          fa: 'برای برنامه‌ریزی عملیات، یک مزرعه انتخاب کنید.',
          en: 'Select a farm to plan operations.',
        ),
      );
    }
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        FilledButton.icon(
          onPressed: onAdd,
          icon: const Icon(Icons.add_task_rounded),
          label: Text(context.l10n.tr(fa: 'برنامه جدید', en: 'New plan')),
        ),
        const SizedBox(height: 12),
        if (plans.isEmpty)
          FarmEmptyView(
            icon: Icons.calendar_month_outlined,
            message: context.l10n.tr(
              fa: 'هنوز عملیاتی برنامه‌ریزی نشده است.',
              en: 'No planned operations yet.',
            ),
          )
        else
          ...plans.map(
            (plan) => Card(
              child: ListTile(
                leading: CircleAvatar(
                  child: Icon(
                    plan.isPlanned
                        ? plan.isOverdue
                            ? Icons.warning_amber_rounded
                            : Icons.event_available_outlined
                        : plan.status == 'completed'
                        ? Icons.check_rounded
                        : Icons.close_rounded,
                  ),
                ),
                title: Text(plan.title),
                subtitle: Text(
                  '${formatDate(context, plan.plannedFor)} • '
                  '${_operationType(context, plan.operationType)}'
                  '${plan.reminderAt == null ? '' : context.l10n.tr(fa: ' • یادآور', en: ' • Reminder')}',
                ),
                trailing:
                    plan.isPlanned
                        ? PopupMenuButton<String>(
                          onSelected:
                              (value) =>
                                  value == 'complete'
                                      ? onComplete(plan)
                                      : onCancel(plan),
                          itemBuilder:
                              (context) => [
                                PopupMenuItem(
                                  value: 'complete',
                                  child: Text(
                                    context.l10n.tr(
                                      fa: 'علامت‌گذاری انجام‌شده',
                                      en: 'Mark complete',
                                    ),
                                  ),
                                ),
                                PopupMenuItem(
                                  value: 'cancel',
                                  child: Text(
                                    context.l10n.tr(
                                      fa: 'لغو برنامه',
                                      en: 'Cancel plan',
                                    ),
                                  ),
                                ),
                              ],
                        )
                        : Text(_planStatus(context, plan.status)),
              ),
            ),
          ),
      ],
    );
  }
}

class _NotebookTab extends StatelessWidget {
  const _NotebookTab({required this.selection, required this.calculations});
  final ToolboxContextSelection? selection;
  final List<FarmToolCalculationModel> calculations;

  @override
  Widget build(BuildContext context) {
    if (selection == null) {
      return FarmEmptyView(
        icon: Icons.menu_book_outlined,
        message: context.l10n.tr(
          fa: 'برای مشاهده دفترچه، یک مزرعه انتخاب کنید.',
          en: 'Select a farm to view the notebook.',
        ),
      );
    }
    if (calculations.isEmpty) {
      return FarmEmptyView(
        icon: Icons.bookmark_border_rounded,
        message: context.l10n.tr(
          fa: 'نتیجه‌ای ذخیره نشده است؛ یک محاسبه‌گر را اجرا و ذخیره کنید.',
          en: 'Nothing saved yet; run a calculator and save its result.',
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: calculations.length,
      itemBuilder: (context, index) {
        final item = calculations[index];
        final definition = calculatorDefinition(item.type);
        return Card(
          child: ExpansionTile(
            leading: CircleAvatar(child: Icon(definition.icon)),
            title: Text(definition.title(context)),
            subtitle: Text(
              '${formatDate(context, item.createdAt, showTime: true)} • '
              '${context.l10n.tr(fa: 'نسخه ${localizeToolboxDigits(context, item.formulaVersion)}', en: 'v${item.formulaVersion}')}',
            ),
            children: [
              for (final result in item.resultValues.entries)
                ListTile(
                  title: Text(definition.resultLabel(context, result.key)),
                  trailing: Text(
                    formatToolboxValue(
                      context,
                      result.value,
                      item.resultUnits[result.key] ?? '',
                    ),
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

class _CostEntrySheet extends StatefulWidget {
  const _CostEntrySheet({required this.selection});
  final ToolboxContextSelection selection;
  @override
  State<_CostEntrySheet> createState() => _CostEntrySheetState();
}

class _CostEntrySheetState extends State<_CostEntrySheet> {
  final _formKey = GlobalKey<FormState>();
  final _amount = TextEditingController();
  final _description = TextEditingController();
  String _type = 'expense';
  String _category = 'other';
  DateTime _date = DateTime.now();

  @override
  void dispose() {
    _amount.dispose();
    _description.dispose();
    super.dispose();
  }

  List<String> get _categories =>
      _type == 'revenue'
          ? const ['harvest_sale', 'other']
          : const [
            'seed',
            'irrigation',
            'fertilizer',
            'pesticide',
            'labor',
            'fuel',
            'machinery',
            'other',
          ];

  @override
  Widget build(BuildContext context) => Padding(
    padding: EdgeInsets.fromLTRB(
      20,
      20,
      20,
      20 + MediaQuery.viewInsetsOf(context).bottom,
    ),
    child: Form(
      key: _formKey,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              context.l10n.tr(fa: 'ثبت مالی جدید', en: 'New financial entry'),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            SegmentedButton<String>(
              segments: [
                ButtonSegment(
                  value: 'expense',
                  label: Text(context.l10n.tr(fa: 'هزینه', en: 'Expense')),
                ),
                ButtonSegment(
                  value: 'revenue',
                  label: Text(context.l10n.tr(fa: 'درآمد', en: 'Revenue')),
                ),
              ],
              selected: {_type},
              onSelectionChanged:
                  (value) => setState(() {
                    _type = value.first;
                    _category = _type == 'revenue' ? 'harvest_sale' : 'other';
                  }),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _category,
              decoration: InputDecoration(
                labelText: context.l10n.tr(fa: 'دسته‌بندی', en: 'Category'),
              ),
              items:
                  _categories
                      .map(
                        (value) => DropdownMenuItem(
                          value: value,
                          child: Text(_financialCategory(context, value)),
                        ),
                      )
                      .toList(),
              onChanged:
                  (value) => setState(() => _category = value ?? 'other'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _amount,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: InputDecoration(
                labelText: context.l10n.tr(fa: 'مبلغ', en: 'Amount'),
                suffixText: context.l10n.tr(fa: 'تومان', en: 'Toman'),
              ),
              validator:
                  (value) =>
                      (parseToolboxNumber(value ?? '') ?? 0) <= 0
                          ? context.l10n.tr(
                            fa: 'مبلغ معتبر وارد کنید',
                            en: 'Enter a valid amount',
                          )
                          : null,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () async {
                final value = await showLocalizedDatePicker(
                  context: context,
                  initialDate: _date,
                  firstDate: DateTime(2000),
                  lastDate: DateTime.now(),
                );
                if (value != null) setState(() => _date = value);
              },
              icon: const Icon(Icons.calendar_today_outlined),
              label: Text(formatDate(context, _date)),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _description,
              maxLength: 500,
              decoration: InputDecoration(
                labelText: context.l10n.tr(
                  fa: 'توضیح (اختیاری)',
                  en: 'Description (optional)',
                ),
              ),
            ),
            FilledButton(
              onPressed: () {
                if (!(_formKey.currentState?.validate() ?? false)) return;
                Navigator.pop(context, {
                  'plot_id': widget.selection.plotId,
                  'cycle_id': widget.selection.cycleId,
                  'entry_type': _type,
                  'category': _category,
                  'amount_toman': parseToolboxNumber(_amount.text),
                  'occurred_on': _isoDate(_date),
                  'description':
                      _description.text.trim().isEmpty
                          ? null
                          : _description.text.trim(),
                });
              },
              child: Text(context.l10n.tr(fa: 'ثبت', en: 'Save')),
            ),
          ],
        ),
      ),
    ),
  );
}

class _PlanEntrySheet extends StatefulWidget {
  const _PlanEntrySheet({required this.selection});
  final ToolboxContextSelection selection;
  @override
  State<_PlanEntrySheet> createState() => _PlanEntrySheetState();
}

class _PlanEntrySheetState extends State<_PlanEntrySheet> {
  final _formKey = GlobalKey<FormState>();
  final _title = TextEditingController();
  final _notes = TextEditingController();
  String _operationType = 'monitoring';
  DateTime _date = DateTime.now();
  bool _reminder = true;

  @override
  void dispose() {
    _title.dispose();
    _notes.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: EdgeInsets.fromLTRB(
      20,
      20,
      20,
      20 + MediaQuery.viewInsetsOf(context).bottom,
    ),
    child: Form(
      key: _formKey,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              context.l10n.tr(
                fa: 'برنامه عملیات جدید',
                en: 'New operation plan',
              ),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _operationType,
              decoration: InputDecoration(
                labelText: context.l10n.tr(
                  fa: 'نوع عملیات',
                  en: 'Operation type',
                ),
              ),
              items:
                  _operationTypes
                      .map(
                        (value) => DropdownMenuItem(
                          value: value,
                          child: Text(_operationTypeLabel(context, value)),
                        ),
                      )
                      .toList(),
              onChanged:
                  (value) =>
                      setState(() => _operationType = value ?? 'monitoring'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _title,
              maxLength: 180,
              decoration: InputDecoration(
                labelText: context.l10n.tr(fa: 'عنوان کار', en: 'Task title'),
              ),
              validator:
                  (value) =>
                      (value ?? '').trim().isEmpty
                          ? context.l10n.tr(
                            fa: 'عنوان را وارد کنید',
                            en: 'Enter a title',
                          )
                          : null,
            ),
            OutlinedButton.icon(
              onPressed: () async {
                final value = await showLocalizedDatePicker(
                  context: context,
                  initialDate: _date,
                  firstDate: DateTime.now().subtract(const Duration(days: 1)),
                  lastDate: DateTime.now().add(const Duration(days: 3650)),
                );
                if (value != null) setState(() => _date = value);
              },
              icon: const Icon(Icons.calendar_today_outlined),
              label: Text(formatDate(context, _date)),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              value: _reminder,
              onChanged: (value) => setState(() => _reminder = value),
              title: Text(
                _date.isAfter(
                      DateTime(
                        DateTime.now().year,
                        DateTime.now().month,
                        DateTime.now().day,
                      ),
                    )
                    ? context.l10n.tr(
                      fa: 'یادآوری یک روز قبل، ساعت ۷',
                      en: 'Remind one day before at 07:00',
                    )
                    : context.l10n.tr(
                      fa: 'یادآوری در اولین نوبت ارسال',
                      en: 'Remind on the next delivery run',
                    ),
              ),
            ),
            TextField(
              controller: _notes,
              maxLength: 5000,
              maxLines: 2,
              decoration: InputDecoration(
                labelText: context.l10n.tr(fa: 'یادداشت', en: 'Notes'),
              ),
            ),
            FilledButton(
              onPressed: () {
                if (!(_formKey.currentState?.validate() ?? false)) return;
                final now = DateTime.now();
                final today = DateTime(now.year, now.month, now.day);
                final reminderAt =
                    _date.isAfter(today)
                        ? DateTime(
                          _date.year,
                          _date.month,
                          _date.day,
                          7,
                        ).subtract(const Duration(days: 1))
                        : now;
                Navigator.pop(context, {
                  'plot_id': widget.selection.plotId,
                  'cycle_id': widget.selection.cycleId,
                  'operation_type': _operationType,
                  'title': _title.text.trim(),
                  'planned_for': _isoDate(_date),
                  'reminder_at':
                      _reminder ? reminderAt.toUtc().toIso8601String() : null,
                  'notes':
                      _notes.text.trim().isEmpty ? null : _notes.text.trim(),
                });
              },
              child: Text(context.l10n.tr(fa: 'ثبت برنامه', en: 'Save plan')),
            ),
          ],
        ),
      ),
    ),
  );
}

const _operationTypes = [
  'land_preparation',
  'planting',
  'irrigation',
  'fertilizing',
  'spraying',
  'weeding',
  'pruning',
  'monitoring',
  'other',
];

String _operationType(BuildContext context, String value) =>
    _operationTypeLabel(context, value);

String _operationTypeLabel(BuildContext context, String value) {
  const fa = {
    'land_preparation': 'آماده‌سازی زمین',
    'planting': 'کاشت',
    'irrigation': 'آبیاری',
    'fertilizing': 'کوددهی',
    'spraying': 'محلول‌پاشی',
    'weeding': 'وجین',
    'pruning': 'هرس',
    'monitoring': 'پایش',
    'other': 'سایر',
  };
  const en = {
    'land_preparation': 'Land preparation',
    'planting': 'Planting',
    'irrigation': 'Irrigation',
    'fertilizing': 'Fertilizing',
    'spraying': 'Spraying',
    'weeding': 'Weeding',
    'pruning': 'Pruning',
    'monitoring': 'Monitoring',
    'other': 'Other',
  };
  return context.l10n.tr(fa: fa[value] ?? value, en: en[value] ?? value);
}

String _financialCategory(BuildContext context, String value) {
  const fa = {
    'seed': 'بذر',
    'irrigation': 'آبیاری',
    'fertilizer': 'کود',
    'pesticide': 'محصول/سم',
    'labor': 'نیروی کار',
    'fuel': 'سوخت',
    'machinery': 'ماشین‌آلات',
    'harvest_sale': 'فروش محصول',
    'other': 'سایر',
  };
  const en = {
    'seed': 'Seed',
    'irrigation': 'Irrigation',
    'fertilizer': 'Fertilizer',
    'pesticide': 'Pesticide/product',
    'labor': 'Labor',
    'fuel': 'Fuel',
    'machinery': 'Machinery',
    'harvest_sale': 'Harvest sale',
    'other': 'Other',
  };
  return context.l10n.tr(fa: fa[value] ?? value, en: en[value] ?? value);
}

String _planStatus(BuildContext context, String value) {
  final fa = value == 'completed' ? 'انجام‌شده' : 'لغوشده';
  final en = value == 'completed' ? 'Completed' : 'Cancelled';
  return context.l10n.tr(fa: fa, en: en);
}

String _isoDate(DateTime value) =>
    '${value.year.toString().padLeft(4, '0')}-'
    '${value.month.toString().padLeft(2, '0')}-'
    '${value.day.toString().padLeft(2, '0')}';

extension _FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
