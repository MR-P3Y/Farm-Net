import 'package:go_router/go_router.dart';

import '../../features/auth/admin_auth_gate.dart';
import '../../features/auth/admin_login_page.dart';
import '../../features/commission/presentation/admin_commission_page.dart';
import '../../features/consultants/presentation/admin_consultants_page.dart';
import '../../features/dashboard/admin_dashboard_page.dart';
import '../../features/media/presentation/admin_media_page.dart';
import '../../features/notifications/presentation/admin_notifications_page.dart';
import '../../features/orders/presentation/admin_orders_page.dart';
import '../../features/products/presentation/admin_products_page.dart';
import '../../features/social/presentation/admin_social_page.dart';
import '../../features/stores/presentation/admin_stores_page.dart';
import '../../features/verifications/presentation/admin_verifications_page.dart';
import '../../features/weather/presentation/admin_weather_page.dart';
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
        GoRoute(
          path: '/orders',
          name: 'admin-orders',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'orders.admin_read',
              child: AdminOrdersPage(),
            );
          },
        ),
        GoRoute(
          path: '/commission',
          name: 'admin-commission',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'commission.read',
              child: AdminCommissionPage(),
            );
          },
        ),
        GoRoute(
          path: '/consultants',
          name: 'admin-consultants',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'consultants.read',
              child: AdminConsultantsPage(),
            );
          },
        ),
        GoRoute(
          path: '/media',
          name: 'admin-media',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'media.admin_read',
              child: AdminMediaPage(),
            );
          },
        ),
        GoRoute(
          path: '/notifications',
          name: 'admin-notifications',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'notifications.admin_read',
              child: AdminNotificationsPage(),
            );
          },
        ),
        GoRoute(
          path: '/weather',
          name: 'admin-weather',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'weather.admin_read',
              child: AdminWeatherPage(),
            );
          },
        ),
        GoRoute(
          path: '/social',
          name: 'admin-social',
          builder: (context, state) {
            return const AdminPermissionGuard(
              permission: 'social.admin_read',
              child: AdminSocialPage(),
            );
          },
        ),
      ],
    ),
  ],
);
