import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/forbidden/admin_forbidden_page.dart';
import 'admin_auth_state.dart';

class AdminPermissionGuard extends ConsumerWidget {
  const AdminPermissionGuard({
    super.key,
    required this.permission,
    required this.child,
  });

  final String permission;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(adminAuthStateProvider);

    if (!auth.hasPermission(permission)) {
      return const AdminForbiddenPage();
    }

    return child;
  }
}
