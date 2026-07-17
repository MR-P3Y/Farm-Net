import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/notification_models.dart';
import '../state/notification_controller.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  bool _loaded = false;
  String? _statusFilter;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(notificationControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() {
    return ref
        .read(notificationControllerProvider.notifier)
        .load(status: _statusFilter);
  }

  Future<void> _openNotification(NotificationModel item) async {
    if (item.isUnread) {
      await ref.read(notificationControllerProvider.notifier).markRead(item.id);
    }

    if (!mounted) return;

    final actionUrl = item.actionUrl;

    if (actionUrl == null || actionUrl.isEmpty) {
      await showDialog<void>(
        context: context,
        builder: (_) => _NotificationDetailDialog(item: item),
      );
      return;
    }

    _goToAction(actionUrl);
  }

  void _goToAction(String actionUrl) {
    if (actionUrl.startsWith('/orders/')) {
      final orderId = actionUrl.split('/').last;
      context.go('/orders/$orderId');
      return;
    }

    if (actionUrl == '/orders') {
      context.go('/orders');
      return;
    }

    if (actionUrl == '/verification' || actionUrl == '/verifications') {
      context.go('/verifications');
      return;
    }

    if (actionUrl == '/media' || actionUrl == '/profile') {
      context.go('/profile');
      return;
    }

    if (actionUrl.startsWith('/social/posts/')) {
      context.go('/social/detail/${actionUrl.split('/').last}');
      return;
    }

    if (actionUrl.startsWith('/services') ||
        actionUrl.startsWith('/consultants')) {
      context.go(actionUrl);
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('مسیر اعلان پشتیبانی نمی‌شود: $actionUrl')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationControllerProvider);

    return Scaffold(
      appBar: FarmAppBar(
        title: 'اعلان‌ها',
        actions: [
          IconButton(
            onPressed: () => context.push('/notifications/preferences'),
            icon: const Icon(Icons.tune_outlined),
            tooltip: 'تنظیمات اعلان‌ها',
          ),
          IconButton(
            onPressed:
                state.isSaving
                    ? null
                    : () {
                      ref
                          .read(notificationControllerProvider.notifier)
                          .markAllRead();
                    },
            icon: const Icon(Icons.done_all_outlined),
            tooltip: 'خواندن همه',
          ),
          IconButton(
            onPressed: _reload,
            icon: const Icon(Icons.refresh),
            tooltip: 'به‌روزرسانی',
          ),
        ],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    children: [
                      _NotificationHeader(
                        unreadCount: state.unreadCount,
                        statusFilter: _statusFilter,
                        onFilterChanged: (value) async {
                          setState(() => _statusFilter = value);
                          await _reload();
                        },
                      ),
                      if (state.errorMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _ErrorMessage(message: state.errorMessage!),
                      ],
                      SizedBox(height: r.v(12)),
                      Expanded(
                        child:
                            state.isLoading
                                ? const FarmLoadingView()
                                : state.items.isEmpty
                                ? const FarmEmptyView(
                                  message: 'فعلاً اعلانی برای نمایش ندارید.',
                                )
                                : RefreshIndicator(
                                  onRefresh: _reload,
                                  child: ListView.separated(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: state.items.length,
                                    separatorBuilder:
                                        (_, __) => SizedBox(height: r.v(10)),
                                    itemBuilder: (context, index) {
                                      final item = state.items[index];

                                      return _NotificationCard(
                                        item: item,
                                        onTap: () => _openNotification(item),
                                        onDelete:
                                            state.isSaving
                                                ? null
                                                : () {
                                                  ref
                                                      .read(
                                                        notificationControllerProvider
                                                            .notifier,
                                                      )
                                                      .deleteNotification(
                                                        item.id,
                                                      );
                                                },
                                      );
                                    },
                                  ),
                                ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _NotificationHeader extends StatelessWidget {
  const _NotificationHeader({
    required this.unreadCount,
    required this.statusFilter,
    required this.onFilterChanged,
  });

  final int unreadCount;
  final String? statusFilter;
  final ValueChanged<String?> onFilterChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            'خوانده‌نشده: $unreadCount',
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
        SizedBox(
          width: 160,
          child: DropdownButtonFormField<String>(
            initialValue: statusFilter ?? 'all',
            decoration: const InputDecoration(
              labelText: 'فیلتر',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'all', child: Text('همه')),
              DropdownMenuItem(value: 'unread', child: Text('خوانده‌نشده')),
              DropdownMenuItem(value: 'read', child: Text('خوانده‌شده')),
              DropdownMenuItem(value: 'archived', child: Text('آرشیو')),
            ],
            onChanged: (value) {
              onFilterChanged(value == 'all' ? null : value);
            },
          ),
        ),
      ],
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({
    required this.item,
    required this.onTap,
    required this.onDelete,
  });

  final NotificationModel item;
  final VoidCallback onTap;
  final VoidCallback? onDelete;

  IconData get _icon {
    if (item.priority == 'urgent') return Icons.priority_high_outlined;
    if (item.priority == 'high') return Icons.warning_amber_outlined;
    if (item.isUnread) return Icons.notifications_active_outlined;
    return Icons.notifications_none_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: item.isUnread ? 2 : 0,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                _icon,
                color:
                    item.isHighPriority
                        ? theme.colorScheme.error
                        : theme.colorScheme.primary,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight:
                            item.isUnread ? FontWeight.w700 : FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      item.body,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      children: [
                        Chip(
                          label: Text(item.status),
                          visualDensity: VisualDensity.compact,
                        ),
                        Chip(
                          label: Text(item.priority),
                          visualDensity: VisualDensity.compact,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: onDelete,
                icon: const Icon(Icons.delete_outline),
                tooltip: 'حذف',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NotificationDetailDialog extends StatelessWidget {
  const _NotificationDetailDialog({required this.item});

  final NotificationModel item;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(item.title),
      content: SingleChildScrollView(child: Text(item.body)),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
      ],
    );
  }
}

class _ErrorMessage extends StatelessWidget {
  const _ErrorMessage({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: AlignmentDirectional.centerStart,
      child: Text(
        message,
        style: TextStyle(color: Theme.of(context).colorScheme.error),
      ),
    );
  }
}
