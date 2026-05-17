import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_store_models.dart';
import '../state/admin_store_controller.dart';

class AdminStoresPage extends ConsumerStatefulWidget {
  const AdminStoresPage({super.key});

  @override
  ConsumerState<AdminStoresPage> createState() => _AdminStoresPageState();
}

class _AdminStoresPageState extends ConsumerState<AdminStoresPage> {
  final _searchController = TextEditingController();
  bool _loaded = false;
  String? _statusFilter;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminStoreControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() async {
    await ref
        .read(adminStoreControllerProvider.notifier)
        .load(status: _statusFilter, q: _searchController.text.trim());
  }

  Future<void> _openDetail(AdminStore item) async {
    await ref.read(adminStoreControllerProvider.notifier).loadDetail(item.id);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _StoreDetailDialog(storeId: item.id),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminStoreControllerProvider);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return Padding(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    'فروشگاه‌ها',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Refresh',
                    onPressed: _reload,
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  SizedBox(
                    width: r.isCompact ? double.infinity : 320,
                    child: TextField(
                      controller: _searchController,
                      decoration: const InputDecoration(
                        labelText: 'جستجو نام یا slug',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _reload(),
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 260,
                    child: DropdownButtonFormField<String?>(
                      value: _statusFilter,
                      decoration: const InputDecoration(
                        labelText: 'وضعیت',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'draft',
                          child: Text('پیش‌نویس'),
                        ),
                        DropdownMenuItem(
                          value: 'pending_review',
                          child: Text('در انتظار بررسی'),
                        ),
                        DropdownMenuItem(
                          value: 'approved',
                          child: Text('تأیید شده'),
                        ),
                        DropdownMenuItem(
                          value: 'rejected',
                          child: Text('رد شده'),
                        ),
                        DropdownMenuItem(
                          value: 'suspended',
                          child: Text('تعلیق شده'),
                        ),
                        DropdownMenuItem(
                          value: 'closed',
                          child: Text('بسته شده'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    height: 56,
                    child: FilledButton.icon(
                      onPressed: _reload,
                      icon: const Icon(Icons.search),
                      label: const Text('جستجو'),
                    ),
                  ),
                ],
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 16),
              Expanded(
                child:
                    state.isLoading
                        ? const AdminLoadingView()
                        : _StoreTable(items: state.items, onOpen: _openDetail),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StoreTable extends StatelessWidget {
  const _StoreTable({required this.items, required this.onOpen});

  final List<AdminStore> items;
  final ValueChanged<AdminStore> onOpen;

  String _statusLabel(String status) {
    switch (status) {
      case 'draft':
        return 'پیش‌نویس';
      case 'pending_review':
        return 'در انتظار بررسی';
      case 'approved':
        return 'تأیید شده';
      case 'rejected':
        return 'رد شده';
      case 'suspended':
        return 'تعلیق شده';
      case 'closed':
        return 'بسته شده';
      default:
        return status;
    }
  }

  String _typeLabel(String type) {
    switch (type) {
      case 'agriculture_inputs':
        return 'نهاده';
      case 'equipment':
        return 'تجهیزات';
      case 'seeds':
        return 'بذر';
      case 'fertilizer':
        return 'کود';
      case 'pesticide':
        return 'سموم';
      case 'mixed':
        return 'چندمنظوره';
      case 'other':
        return 'سایر';
      default:
        return type;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'فروشگاهی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('نام')),
          DataColumn(label: Text('مالک')),
          DataColumn(label: Text('نوع')),
          DataColumn(label: Text('وضعیت')),
          DataColumn(label: Text('عملیات')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.name)),
                  DataCell(Text(item.ownerEmail ?? item.ownerPhone ?? '-')),
                  DataCell(Text(_typeLabel(item.storeType))),
                  DataCell(Text(_statusLabel(item.status))),
                  DataCell(
                    TextButton(
                      onPressed: () => onOpen(item),
                      child: const Text('بررسی'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }
}

class _StoreDetailDialog extends ConsumerStatefulWidget {
  const _StoreDetailDialog({required this.storeId});

  final int storeId;

  @override
  ConsumerState<_StoreDetailDialog> createState() => _StoreDetailDialogState();
}

class _StoreDetailDialogState extends ConsumerState<_StoreDetailDialog> {
  final _noteController = TextEditingController();

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _updateStatus(String status) async {
    final ok = await ref
        .read(adminStoreControllerProvider.notifier)
        .updateStatus(
          storeId: widget.storeId,
          status: status,
          note: _noteController.text.trim(),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminStoreControllerProvider);
    final store = state.selected;

    if (store == null) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    return AlertDialog(
      title: Text('بررسی فروشگاه #${store.id}'),
      content: SizedBox(
        width: 760,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('نام: ${store.name}'),
              const SizedBox(height: 8),
              Text('Slug: ${store.slug}'),
              const SizedBox(height: 8),
              Text(
                'مالک: ${store.ownerEmail ?? store.ownerPhone ?? store.ownerUserId}',
              ),
              const SizedBox(height: 8),
              Text('وضعیت: ${store.status}'),
              const SizedBox(height: 8),
              Text('نوع: ${store.storeType}'),
              const SizedBox(height: 8),
              Text('آدرس: ${store.address ?? '-'}'),
              const SizedBox(height: 8),
              Text('توضیحات: ${store.description ?? '-'}'),
              const Divider(height: 28),
              Text('اعضا', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (store.members.isEmpty)
                const Text('عضوی ثبت نشده است.')
              else
                ...store.members.map(
                  (member) => ListTile(
                    dense: true,
                    leading: const Icon(Icons.person_outline),
                    title: Text('user_id: ${member.userId}'),
                    subtitle: Text('${member.role} - ${member.status}'),
                  ),
                ),
              const Divider(height: 28),
              Text(
                'تاریخچه وضعیت',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              if (store.statusHistory.isEmpty)
                const Text('تاریخچه‌ای ثبت نشده است.')
              else
                ...store.statusHistory.map(
                  (row) => ListTile(
                    dense: true,
                    leading: const Icon(Icons.history),
                    title: Text('${row.fromStatus ?? '-'} -> ${row.toStatus}'),
                    subtitle: Text(row.note ?? '-'),
                  ),
                ),
              const Divider(height: 28),
              TextField(
                controller: _noteController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'یادداشت ادمین',
                  border: OutlineInputBorder(),
                ),
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: state.isSaving ? null : () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
        OutlinedButton(
          onPressed: state.isSaving ? null : () => _updateStatus('rejected'),
          child: const Text('رد'),
        ),
        OutlinedButton(
          onPressed: state.isSaving ? null : () => _updateStatus('suspended'),
          child: const Text('تعلیق'),
        ),
        FilledButton(
          onPressed: state.isSaving ? null : () => _updateStatus('approved'),
          child:
              state.isSaving
                  ? const SizedBox.square(
                    dimension: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                  : const Text('تأیید'),
        ),
      ],
    );
  }
}
