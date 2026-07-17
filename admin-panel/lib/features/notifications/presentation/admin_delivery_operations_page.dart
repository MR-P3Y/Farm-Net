import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_notification_api.dart';
import '../data/admin_notification_models.dart';
import '../data/admin_notification_repository.dart';

class AdminDeliveryOperationsPage extends ConsumerStatefulWidget {
  const AdminDeliveryOperationsPage({super.key});

  @override
  ConsumerState<AdminDeliveryOperationsPage> createState() =>
      _AdminDeliveryOperationsPageState();
}

class _AdminDeliveryOperationsPageState
    extends ConsumerState<AdminDeliveryOperationsPage> {
  bool _loading = true;
  String? _error;
  String? _status;
  String? _channel;
  int _page = 1;
  int _totalPages = 1;
  List<AdminDeliveryModel> _items = const [];

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
      final result = await ref
          .read(adminNotificationRepositoryProvider)
          .listDeliveries(page: _page, status: _status, channel: _channel);
      if (!mounted) return;
      setState(() {
        _items = result.items;
        _page = result.page;
        _totalPages = result.totalPages < 1 ? 1 : result.totalPages;
      });
    } on AdminNotificationApiException catch (error) {
      if (mounted) setState(() => _error = error.error.message);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _openDetail(AdminDeliveryModel row) async {
    try {
      final detail = await ref
          .read(adminNotificationRepositoryProvider)
          .getDelivery(row.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder:
            (_) => _DeliveryDetailDialog(
              delivery: detail,
              onRetry: detail.canRetry ? () => _retry(detail.id) : null,
            ),
      );
    } on AdminNotificationApiException catch (error) {
      _showError(error.error.message);
    }
  }

  Future<void> _retry(int id) async {
    try {
      await ref.read(adminNotificationRepositoryProvider).retryDelivery(id);
      if (!mounted) return;
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ارسال مجدد در صف قرار گرفت.')),
      );
      await _load();
    } on AdminNotificationApiException catch (error) {
      _showError(error.error.message);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'عملیات ارسال اعلان‌ها',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _loading ? null : _load,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _filter(
                label: 'Status',
                value: _status,
                values: const [
                  'pending',
                  'processing',
                  'sent',
                  'delivered',
                  'failed',
                  'skipped',
                ],
                onChanged: (value) {
                  setState(() {
                    _status = value;
                    _page = 1;
                  });
                  _load();
                },
              ),
              _filter(
                label: 'Channel',
                value: _channel,
                values: const ['email', 'sms', 'push'],
                onChanged: (value) {
                  setState(() {
                    _channel = value;
                    _page = 1;
                  });
                  _load();
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(child: _body()),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed:
                    !_loading && _page > 1
                        ? () {
                          setState(() => _page--);
                          _load();
                        }
                        : null,
                icon: const Icon(Icons.chevron_left),
              ),
              Text('صفحه $_page از $_totalPages'),
              IconButton(
                onPressed:
                    !_loading && _page < _totalPages
                        ? () {
                          setState(() => _page++);
                          _load();
                        }
                        : null,
                icon: const Icon(Icons.chevron_right),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _filter({
    required String label,
    required String? value,
    required List<String> values,
    required ValueChanged<String?> onChanged,
  }) {
    return SizedBox(
      width: 220,
      child: DropdownButtonFormField<String?>(
        initialValue: value,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        items: [
          const DropdownMenuItem<String?>(value: null, child: Text('همه')),
          ...values.map(
            (item) => DropdownMenuItem(value: item, child: Text(item)),
          ),
        ],
        onChanged: onChanged,
      ),
    );
  }

  Widget _body() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!),
            const SizedBox(height: 8),
            OutlinedButton(onPressed: _load, child: const Text('تلاش مجدد')),
          ],
        ),
      );
    }
    if (_items.isEmpty) return const Center(child: Text('ارسالی یافت نشد.'));
    return ListView.separated(
      itemCount: _items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final item = _items[index];
        return Card(
          child: ListTile(
            onTap: () => _openDetail(item),
            leading: const Icon(Icons.outbox_outlined),
            title: Text('#${item.id} • ${item.channel} • ${item.status}'),
            subtitle: Text(
              'Notification #${item.notificationId} | تلاش ${item.attemptCount}/${item.maxAttempts}',
            ),
            trailing: const Icon(Icons.chevron_right),
          ),
        );
      },
    );
  }
}

class _DeliveryDetailDialog extends StatelessWidget {
  const _DeliveryDetailDialog({required this.delivery, this.onRetry});

  final AdminDeliveryModel delivery;
  final Future<void> Function()? onRetry;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('ارسال #${delivery.id}'),
      content: SizedBox(
        width: 560,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('کانال: ${delivery.channel}'),
              Text('وضعیت: ${delivery.status}'),
              Text('Provider: ${delivery.provider ?? '-'}'),
              if (delivery.errorCode != null)
                Text(
                  'خطا: ${delivery.errorCode} — ${delivery.errorMessage ?? ''}',
                ),
              const Divider(height: 28),
              Text(
                'تاریخچه تلاش‌ها',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              if (delivery.attempts.isEmpty)
                const Text('هنوز تلاشی ثبت نشده است.'),
              ...delivery.attempts.map(
                (attempt) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.timeline),
                  title: Text(
                    'تلاش ${attempt.attemptNumber}: ${attempt.status}',
                  ),
                  subtitle: Text(
                    '${attempt.startedAt}${attempt.errorMessage == null ? '' : '\n${attempt.errorMessage}'}',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
        if (onRetry != null)
          FilledButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.replay),
            label: const Text('ارسال مجدد'),
          ),
      ],
    );
  }
}
