import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../home/state/home_dashboard_controller.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';
import 'farm_profile_editor_screen.dart';
import 'widgets/farm_profile_action_dialogs.dart';

class MyFarmsScreen extends ConsumerStatefulWidget {
  const MyFarmsScreen({super.key});

  @override
  ConsumerState<MyFarmsScreen> createState() => _MyFarmsScreenState();
}

class _MyFarmsScreenState extends ConsumerState<MyFarmsScreen> {
  List<FarmModel>? _items;
  Object? _error;
  bool _includeArchived = false;
  int? _busyFarmId;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _error = null);
    try {
      final items = await ref
          .read(farmRepositoryProvider)
          .farms(includeArchived: _includeArchived);
      if (mounted) setState(() => _items = items);
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _create() async {
    final created = await Navigator.of(context).push<FarmModel>(
      MaterialPageRoute(builder: (_) => const FarmProfileEditorScreen()),
    );
    if (created != null) await _refreshAfterMutation();
  }

  Future<void> _edit(FarmModel farm) async {
    final updated = await Navigator.of(context).push<FarmModel>(
      MaterialPageRoute(builder: (_) => FarmProfileEditorScreen(farm: farm)),
    );
    if (updated != null) await _refreshAfterMutation();
  }

  Future<void> _archive(FarmModel farm) async {
    final request = await showFarmArchiveDialog(context, farm);
    if (request == null || !mounted) return;
    setState(() => _busyFarmId = farm.id);
    try {
      await ref
          .read(farmRepositoryProvider)
          .archiveFarm(farm.id, reason: request.reason);
      await _refreshAfterMutation();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              context.l10n.tr(
                fa: 'مزرعه از فهرست فعال حذف و بایگانی شد.',
                en: 'The farm was removed from the active list and archived.',
              ),
            ),
          ),
        );
      }
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) setState(() => _busyFarmId = null);
    }
  }

  Future<void> _restore(FarmModel farm) async {
    if (!await showFarmRestoreDialog(context, farm) || !mounted) return;
    setState(() => _busyFarmId = farm.id);
    try {
      await ref.read(farmRepositoryProvider).restoreFarm(farm.id);
      await _refreshAfterMutation();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              context.l10n.tr(
                fa: 'مزرعه با موفقیت بازیابی شد.',
                en: 'The farm was restored.',
              ),
            ),
          ),
        );
      }
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) setState(() => _busyFarmId = null);
    }
  }

  Future<void> _open(FarmModel farm) async {
    await context.push('/farms/${farm.id}', extra: farm);
    if (mounted) await _refreshAfterMutation();
  }

  Future<void> _refreshAfterMutation() async {
    await _load();
    await ref.read(homeDashboardControllerProvider.notifier).refresh();
  }

  void _showError(Object error) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          context.l10n.tr(
            fa: 'انجام عملیات مزرعه ممکن نشد: $error',
            en: 'The Farm action could not be completed: $error',
          ),
        ),
      ),
    );
  }

  Future<void> _toggleArchived(bool value) async {
    setState(() {
      _includeArchived = value;
      _items = null;
    });
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: FarmAppBar(title: l10n.tr(fa: 'مزرعه‌های من', en: 'My farms')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _create,
        icon: const Icon(Icons.add),
        label: Text(l10n.tr(fa: 'مزرعه جدید', en: 'Add farm')),
      ),
      body: Column(
        children: [
          SwitchListTile.adaptive(
            value: _includeArchived,
            onChanged: _toggleArchived,
            secondary: const Icon(Icons.inventory_2_outlined),
            title: Text(
              l10n.tr(fa: 'نمایش مزرعه‌های حذف‌شده', en: 'Show removed farms'),
            ),
            subtitle: Text(
              l10n.tr(
                fa: 'مزرعه‌های بایگانی‌شده را می‌توانید بازیابی کنید.',
                en: 'Archived Farms can be restored.',
              ),
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child:
                _error != null
                    ? _ErrorState(error: _error!, onRetry: _load)
                    : _items == null
                    ? const FarmLoadingView()
                    : _items!.isEmpty
                    ? FarmEmptyView(
                      message:
                          _includeArchived
                              ? l10n.tr(
                                fa: 'مزرعه‌ای برای نمایش وجود ندارد',
                                en: 'No Farms to show',
                              )
                              : l10n.tr(
                                fa: 'هنوز مزرعه‌ای ثبت نشده است',
                                en: 'No Farm has been added yet',
                              ),
                    )
                    : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        physics: const AlwaysScrollableScrollPhysics(),
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                        itemCount: _items!.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, index) {
                          final farm = _items![index];
                          return _FarmCard(
                            farm: farm,
                            busy: _busyFarmId == farm.id,
                            onOpen: farm.isArchived ? null : () => _open(farm),
                            onEdit: farm.canEdit ? () => _edit(farm) : null,
                            onArchive:
                                farm.canArchive ? () => _archive(farm) : null,
                            onRestore:
                                farm.canRestore ? () => _restore(farm) : null,
                          );
                        },
                      ),
                    ),
          ),
        ],
      ),
    );
  }
}

class _FarmCard extends StatelessWidget {
  const _FarmCard({
    required this.farm,
    required this.busy,
    this.onOpen,
    this.onEdit,
    this.onArchive,
    this.onRestore,
  });

  final FarmModel farm;
  final bool busy;
  final VoidCallback? onOpen;
  final VoidCallback? onEdit;
  final VoidCallback? onArchive;
  final VoidCallback? onRestore;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final area = farm.declaredAreaSqm;
    final rawArea =
        area == null
            ? null
            : area >= 10000
            ? (area / 10000).toStringAsFixed(2)
            : area.toStringAsFixed(0);
    final localizedArea =
        rawArea != null && l10n.isFa ? toPersianDigits(rawArea) : rawArea;
    final areaLabel =
        area == null
            ? l10n.tr(fa: 'مساحت کل ثبت نشده', en: 'Total area not set')
            : area >= 10000
            ? l10n.tr(fa: '$localizedArea هکتار', en: '$localizedArea ha')
            : l10n.tr(fa: '$localizedArea متر مربع', en: '$localizedArea m²');
    return Card(
      child: ListTile(
        enabled: !busy,
        leading: CircleAvatar(
          child: Icon(
            farm.isArchived
                ? Icons.inventory_2_outlined
                : Icons.agriculture_outlined,
          ),
        ),
        title: Row(
          children: [
            Expanded(child: Text(farm.name)),
            if (farm.isArchived)
              Chip(
                visualDensity: VisualDensity.compact,
                label: Text(l10n.tr(fa: 'حذف‌شده', en: 'Removed')),
              ),
          ],
        ),
        subtitle: Text(
          farm.description == null || farm.description!.isEmpty
              ? areaLabel
              : '$areaLabel\n${farm.description}',
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
        isThreeLine: farm.description?.isNotEmpty ?? false,
        trailing:
            busy
                ? const SizedBox.square(
                  dimension: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
                : PopupMenuButton<_FarmMenuAction>(
                  tooltip: l10n.tr(fa: 'مدیریت مزرعه', en: 'Manage farm'),
                  onSelected: (action) {
                    final callback = switch (action) {
                      _FarmMenuAction.edit => onEdit,
                      _FarmMenuAction.archive => onArchive,
                      _FarmMenuAction.restore => onRestore,
                    };
                    callback?.call();
                  },
                  itemBuilder:
                      (_) => [
                        if (onEdit != null)
                          PopupMenuItem(
                            value: _FarmMenuAction.edit,
                            child: ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(Icons.edit_outlined),
                              title: Text(l10n.tr(fa: 'ویرایش', en: 'Edit')),
                            ),
                          ),
                        if (onArchive != null)
                          PopupMenuItem(
                            value: _FarmMenuAction.archive,
                            child: ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: Icon(
                                Icons.delete_outline_rounded,
                                color: Theme.of(context).colorScheme.error,
                              ),
                              title: Text(
                                l10n.tr(fa: 'حذف مزرعه', en: 'Remove farm'),
                              ),
                            ),
                          ),
                        if (onRestore != null)
                          PopupMenuItem(
                            value: _FarmMenuAction.restore,
                            child: ListTile(
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(Icons.restore_rounded),
                              title: Text(
                                l10n.tr(fa: 'بازیابی', en: 'Restore'),
                              ),
                            ),
                          ),
                      ],
                ),
        onTap: onOpen,
      ),
    );
  }
}

enum _FarmMenuAction { edit, archive, restore }

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
