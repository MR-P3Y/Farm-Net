import 'package:go_router/go_router.dart';

import '../../features/auth/admin_auth_gate.dart';
import '../../features/auth/admin_login_page.dart';
import '../../features/dashboard/admin_dashboard_page.dart';
import '../auth/admin_permission_guard.dart';
import '../widgets/admin_app_shell.dart';

final GoRouter adminRouter = GoRouter(
  initialLocation: '/dashboard',
  routes: [
    GoRoute(
      path: '/login',
      name: 'admin-login',
      builder: (context, state) => const AdminLoginPage(),
    ),
    ShellRoute(
      builder: (context, state, child) {
        return AdminAuthGate(child: AdminAppShell(child: child));
      },
      routes: [
        GoRoute(
          path: '/dashboard',
          name: 'admin-dashboard',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'dashboard.read',
              child: AdminDashboardPage(),
            );
          },
        ),
      ],
    ),
  ],
);
