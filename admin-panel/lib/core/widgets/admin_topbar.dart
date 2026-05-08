import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/state/admin_auth_controller.dart';
import '../auth/admin_auth_state.dart';
import '../localization/admin_localizations.dart';

class AdminTopbar extends ConsumerWidget {
  const AdminTopbar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AdminLocalizations.of(context);
    final auth = ref.watch(adminAuthStateProvider);
    final user = auth.user;

    return Container(
      height: 64,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor.withValues(alpha: 0.2),
          ),
        ),
      ),
      child: Row(
        children: [
          Text(l10n.appName, style: Theme.of(context).textTheme.titleMedium),
          const Spacer(),
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.notifications_none),
          ),
          const SizedBox(width: 8),
          if (user != null)
            Text(
              user.email ?? user.phone ?? '',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          const SizedBox(width: 12),
          IconButton(
            tooltip: 'Logout',
            onPressed: () {
              ref.read(adminAuthControllerProvider).logout();
            },
            icon: const Icon(Icons.logout),
          ),
          const SizedBox(width: 8),
          const CircleAvatar(child: Icon(Icons.person_outline)),
        ],
      ),
    );
  }
}
