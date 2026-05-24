import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_notification_models.dart';
import '../state/admin_notification_controller.dart';

class AdminNotificationsPage extends ConsumerStatefulWidget {
  const AdminNotificationsPage({super.key});

  @override
  ConsumerState<AdminNotificationsPage> createState() =>
      _AdminNotificationsPageState();
}

class _AdminNotificationsPageState
    extends ConsumerState<AdminNotificationsPage> {
  bool _loaded = false;
  String? _statusFilter;
  String? _channelFilter;
  final _recipientFilterController = TextEditingController();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminNotificationControllerProvider.notifier).load();
    });
  }

  @override
  void dispose() {
    _recipientFilterController.dispose();
    super.dispose();
  }

  Future<void> _reload() {
    final recipientText = _recipientFilterController.text.trim();
    final recipientId =
        recipientText.isEmpty ? null : int.tryParse(recipientText);

    return ref
        .read(adminNotificationControllerProvider.notifier)
        .load(
          status: _statusFilter,
          channel: _channelFilter,
          recipientUserId: recipientId,
        );
  }

  Future<void> _openDetail(AdminNotificationModel item) async {
    await ref
        .read(adminNotificationControllerProvider.notifier)
        .loadDetail(item.id);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _NotificationDetailDialog(id: item.id),
    );
  }

  Future<void> _openSystemMessageDialog() async {
    await showDialog<void>(
      context: context,
      builder: (_) => const _SystemMessageDialog(),
    );

    await _reload();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminNotificationControllerProvider);

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
                    'مدیریت اعلان‌ها',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  FilledButton.icon(
                    onPressed: state.isSaving ? null : _openSystemMessageDialog,
                    icon: const Icon(Icons.add_comment_outlined),
                    label: const Text('پیام سیستمی'),
                  ),
                  const SizedBox(width: 8),
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
                    width: r.isCompact ? double.infinity : 220,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _statusFilter,
                      decoration: const InputDecoration(
                        labelText: 'Status',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'unread',
                          child: Text('unread'),
                        ),
                        DropdownMenuItem(value: 'read', child: Text('read')),
                        DropdownMenuItem(
                          value: 'archived',
                          child: Text('archived'),
                        ),
                        DropdownMenuItem(
                          value: 'deleted',
                          child: Text('deleted'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 220,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _channelFilter,
                      decoration: const InputDecoration(
                        labelText: 'Channel',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'in_app',
                          child: Text('in_app'),
                        ),
                        DropdownMenuItem(value: 'sms', child: Text('sms')),
                        DropdownMenuItem(value: 'email', child: Text('email')),
                        DropdownMenuItem(value: 'push', child: Text('push')),
                        DropdownMenuItem(
                          value: 'telegram',
                          child: Text('telegram'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _channelFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 240,
                    child: TextField(
                      controller: _recipientFilterController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Recipient user id',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _reload(),
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
                        : _NotificationsTable(
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

class _NotificationsTable extends StatelessWidget {
  const _NotificationsTable({required this.items, required this.onOpen});

  final List<AdminNotificationModel> items;
  final ValueChanged<AdminNotificationModel> onOpen;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'اعلانی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('Recipient')),
          DataColumn(label: Text('Title')),
          DataColumn(label: Text('Channel')),
          DataColumn(label: Text('Priority')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Action')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.recipientUserId.toString())),
                  DataCell(Text(item.title)),
                  DataCell(Text(item.channel)),
                  DataCell(Text(item.priority)),
                  DataCell(Text(item.status)),
                  DataCell(
                    TextButton(
                      onPressed: () => onOpen(item),
                      child: const Text('جزئیات'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }
}

class _NotificationDetailDialog extends ConsumerWidget {
  const _NotificationDetailDialog({required this.id});

  final int id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(adminNotificationControllerProvider);
    final item = state.selected;

    if (item == null || item.id != id) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    return AlertDialog(
      title: Text('اعلان #${item.id}'),
      content: SizedBox(
        width: 720,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.72,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _DetailLine(
                  label: 'Recipient',
                  value: item.recipientUserId.toString(),
                ),
                _DetailLine(label: 'Channel', value: item.channel),
                _DetailLine(label: 'Priority', value: item.priority),
                _DetailLine(label: 'Status', value: item.status),
                if (item.eventId != null)
                  _DetailLine(label: 'Event ID', value: '${item.eventId}'),
                if (item.actionUrl != null)
                  _DetailLine(label: 'Action URL', value: item.actionUrl!),
                const Divider(height: 28),
                Text(
                  item.title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                SelectableText(item.body),
                const Divider(height: 28),
                _DetailLine(label: 'Created', value: item.createdAt),
                _DetailLine(label: 'Updated', value: item.updatedAt),
                if (item.readAt != null)
                  _DetailLine(label: 'Read', value: item.readAt!),
                if (item.deletedAt != null)
                  _DetailLine(label: 'Deleted', value: item.deletedAt!),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
      ],
    );
  }
}

class _SystemMessageDialog extends ConsumerStatefulWidget {
  const _SystemMessageDialog();

  @override
  ConsumerState<_SystemMessageDialog> createState() =>
      _SystemMessageDialogState();
}

class _SystemMessageDialogState extends ConsumerState<_SystemMessageDialog> {
  final _recipientController = TextEditingController();
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();
  final _actionUrlController = TextEditingController();

  String _priority = 'normal';

  @override
  void dispose() {
    _recipientController.dispose();
    _titleController.dispose();
    _bodyController.dispose();
    _actionUrlController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final recipientId = int.tryParse(_recipientController.text.trim());

    if (recipientId == null || recipientId <= 0) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('شناسه کاربر معتبر نیست.')));
      return;
    }

    final title = _titleController.text.trim();
    final body = _bodyController.text.trim();

    if (title.isEmpty || body.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('عنوان و متن پیام الزامی است.')),
      );
      return;
    }

    final actionUrl = _actionUrlController.text.trim();
    final ok = await ref
        .read(adminNotificationControllerProvider.notifier)
        .createSystemMessage(
          recipientUserId: recipientId,
          title: title,
          body: body,
          actionUrl: actionUrl.isEmpty ? null : actionUrl,
          priority: _priority,
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminNotificationControllerProvider);

    return AlertDialog(
      title: const Text('ارسال پیام سیستمی'),
      content: SizedBox(
        width: 620,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _recipientController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'شناسه کاربر گیرنده',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'عنوان',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _bodyController,
                maxLines: 5,
                decoration: const InputDecoration(
                  labelText: 'متن پیام',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _actionUrlController,
                decoration: const InputDecoration(
                  labelText: 'Action URL اختیاری',
                  hintText: '/orders یا /profile',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _priority,
                decoration: const InputDecoration(
                  labelText: 'Priority',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'low', child: Text('low')),
                  DropdownMenuItem(value: 'normal', child: Text('normal')),
                  DropdownMenuItem(value: 'high', child: Text('high')),
                  DropdownMenuItem(value: 'urgent', child: Text('urgent')),
                ],
                onChanged: (value) {
                  if (value == null) return;
                  setState(() => _priority = value);
                },
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
          child: const Text('انصراف'),
        ),
        FilledButton.icon(
          onPressed: state.isSaving ? null : _submit,
          icon: const Icon(Icons.send_outlined),
          label: const Text('ارسال'),
        ),
      ],
    );
  }
}

class _DetailLine extends StatelessWidget {
  const _DetailLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 140, child: Text(label)),
          Expanded(child: SelectableText(value)),
        ],
      ),
    );
  }
}
