import 'package:go_router/go_router.dart';

import '../../features/auth/admin_auth_gate.dart';
import '../../features/auth/admin_login_page.dart';
import '../../features/dashboard/admin_dashboard_page.dart';
import '../../features/products/presentation/admin_products_page.dart';
import '../../features/stores/presentation/admin_stores_page.dart';
import '../../features/verifications/presentation/admin_verifications_page.dart';
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
        GoRoute(
          path: '/verifications',
          name: 'admin-verifications',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'verification.read',
              child: AdminVerificationsPage(),
            );
          },
        ),
        GoRoute(
          path: '/stores',
          name: 'admin-stores',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'stores.admin_read',
              child: AdminStoresPage(),
            );
          },
        ),
        GoRoute(
          path: '/products',
          name: 'admin-products',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'products.admin_read',
              child: AdminProductsPage(),
            );
          },
        ),
      ],
    ),
  ],
);
