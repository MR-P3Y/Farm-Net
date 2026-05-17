import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_verification_models.dart';
import '../state/admin_verification_controller.dart';

class AdminVerificationsPage extends ConsumerStatefulWidget {
  const AdminVerificationsPage({super.key});

  @override
  ConsumerState<AdminVerificationsPage> createState() =>
      _AdminVerificationsPageState();
}

class _AdminVerificationsPageState
    extends ConsumerState<AdminVerificationsPage> {
  bool _loaded = false;
  String? _statusFilter;
  String? _targetRoleFilter;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminVerificationControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() async {
    await ref
        .read(adminVerificationControllerProvider.notifier)
        .load(status: _statusFilter, targetRole: _targetRoleFilter);
  }

  Future<void> _openDetail(AdminVerificationRequest item) async {
    await ref
        .read(adminVerificationControllerProvider.notifier)
        .loadDetail(item.id);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _VerificationDetailDialog(requestId: item.id),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminVerificationControllerProvider);

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
                    'درخواست‌های تأیید',
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
                          value: 'submitted',
                          child: Text('ارسال‌شده'),
                        ),
                        DropdownMenuItem(
                          value: 'under_review',
                          child: Text('در حال بررسی'),
                        ),
                        DropdownMenuItem(
                          value: 'needs_revision',
                          child: Text('نیازمند اصلاح'),
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
                          value: 'cancelled',
                          child: Text('لغو شده'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 260,
                    child: DropdownButtonFormField<String?>(
                      value: _targetRoleFilter,
                      decoration: const InputDecoration(
                        labelText: 'نقش',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'shop_owner',
                          child: Text('فروشگاه‌دار'),
                        ),
                        DropdownMenuItem(
                          value: 'lessor',
                          child: Text('موجر ادوات'),
                        ),
                        DropdownMenuItem(
                          value: 'consultant',
                          child: Text('مشاور'),
                        ),
                        DropdownMenuItem(
                          value: 'service_provider',
                          child: Text('ارائه‌دهنده خدمات'),
                        ),
                        DropdownMenuItem(
                          value: 'data_client',
                          child: Text('مشتری داده'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _targetRoleFilter = value);
                        await _reload();
                      },
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
                        : _VerificationTable(
                          items: state.items,
                          onOpen: _openDetail,
                        ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _VerificationTable extends StatelessWidget {
  const _VerificationTable({required this.items, required this.onOpen});

  final List<AdminVerificationRequest> items;
  final ValueChanged<AdminVerificationRequest> onOpen;

  String _roleLabel(String role) {
    switch (role) {
      case 'shop_owner':
        return 'فروشگاه‌دار';
      case 'lessor':
        return 'موجر ادوات';
      case 'consultant':
        return 'مشاور';
      case 'service_provider':
        return 'خدمات';
      case 'data_client':
        return 'مشتری داده';
      default:
        return role;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'draft':
        return 'پیش‌نویس';
      case 'submitted':
        return 'ارسال‌شده';
      case 'under_review':
        return 'در حال بررسی';
      case 'needs_revision':
        return 'نیازمند اصلاح';
      case 'approved':
        return 'تأیید شده';
      case 'rejected':
        return 'رد شده';
      case 'cancelled':
        return 'لغو شده';
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'درخواستی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('کاربر')),
          DataColumn(label: Text('نقش')),
          DataColumn(label: Text('وضعیت')),
          DataColumn(label: Text('مدارک')),
          DataColumn(label: Text('عملیات')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.userEmail ?? item.userPhone ?? '-')),
                  DataCell(Text(_roleLabel(item.targetRole))),
                  DataCell(Text(_statusLabel(item.status))),
                  DataCell(Text(item.documents.length.toString())),
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

class _VerificationDetailDialog extends ConsumerStatefulWidget {
  const _VerificationDetailDialog({required this.requestId});

  final int requestId;

  @override
  ConsumerState<_VerificationDetailDialog> createState() =>
      _VerificationDetailDialogState();
}

class _VerificationDetailDialogState
    extends ConsumerState<_VerificationDetailDialog> {
  final _noteController = TextEditingController();

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _updateStatus(String status) async {
    final ok = await ref
        .read(adminVerificationControllerProvider.notifier)
        .updateStatus(
          requestId: widget.requestId,
          status: status,
          note: _noteController.text.trim(),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminVerificationControllerProvider);
    final item = state.selected;

    if (item == null) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    return AlertDialog(
      title: Text('بررسی درخواست #${item.id}'),
      content: SizedBox(
        width: 720,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('کاربر: ${item.userEmail ?? item.userPhone ?? item.userId}'),
              const SizedBox(height: 8),
              Text('نقش: ${item.targetRole}'),
              const SizedBox(height: 8),
              Text('وضعیت فعلی: ${item.status}'),
              const SizedBox(height: 8),
              Text('توضیح کاربر: ${item.requestNote ?? '-'}'),
              const Divider(height: 28),
              Text('مدارک', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (item.documents.isEmpty)
                const Text('مدرکی ثبت نشده است.')
              else
                ...item.documents.map(
                  (doc) => ListTile(
                    dense: true,
                    leading: const Icon(Icons.description_outlined),
                    title: Text(doc.fileName),
                    subtitle: Text('${doc.documentType} - ${doc.status}'),
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
          onPressed:
              state.isSaving ? null : () => _updateStatus('under_review'),
          child: const Text('در حال بررسی'),
        ),
        OutlinedButton(
          onPressed:
              state.isSaving ? null : () => _updateStatus('needs_revision'),
          child: const Text('نیازمند اصلاح'),
        ),
        OutlinedButton(
          onPressed: state.isSaving ? null : () => _updateStatus('rejected'),
          child: const Text('رد'),
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
