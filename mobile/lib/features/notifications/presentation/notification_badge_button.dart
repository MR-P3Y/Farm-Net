import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../state/notification_controller.dart';

class NotificationBadgeButton extends ConsumerStatefulWidget {
  const NotificationBadgeButton({required this.onPressed, super.key});

  final VoidCallback onPressed;

  @override
  ConsumerState<NotificationBadgeButton> createState() =>
      _NotificationBadgeButtonState();
}

class _NotificationBadgeButtonState
    extends ConsumerState<NotificationBadgeButton> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(notificationControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = ref.watch(
      notificationControllerProvider.select((state) => state.unreadCount),
    );

    return Stack(
      clipBehavior: Clip.none,
      children: [
        IconButton(
          onPressed: widget.onPressed,
          icon: const Icon(Icons.notifications_none_outlined),
          tooltip: 'اعلان‌ها',
        ),
        if (unreadCount > 0)
          PositionedDirectional(
            top: 6,
            end: 6,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.error,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                unreadCount > 99 ? '99+' : unreadCount.toString(),
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onError,
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
      ],
    );
  }
}
