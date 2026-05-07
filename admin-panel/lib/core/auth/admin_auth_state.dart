import 'package:flutter_riverpod/flutter_riverpod.dart';

final adminAuthStateProvider =
    StateNotifierProvider<AdminAuthStateController, AdminAuthState>(
  (ref) => AdminAuthStateController(),
);

class AdminAuthState {
  const AdminAuthState({
    required this.isAuthenticated,
    required this.permissions,
  });

  final bool isAuthenticated;
  final Set<String> permissions;

  bool hasPermission(String permission) {
    return permissions.contains(permission);
  }

  bool hasAnyPermission(List<String> items) {
    return items.any(permissions.contains);
  }
}

class AdminAuthStateController extends StateNotifier<AdminAuthState> {
  AdminAuthStateController()
      : super(
          const AdminAuthState(
            isAuthenticated: false,
            permissions: {},
          ),
        );

  void mockLoginAsSuperAdmin() {
    state = const AdminAuthState(
      isAuthenticated: true,
      permissions: {
        'dashboard.read',
        'users.read',
        'shops.read',
        'products.read',
        'finance.invoices.read',
        'settings.read',
      },
    );
  }

  void logout() {
    state = const AdminAuthState(
      isAuthenticated: false,
      permissions: {},
    );
  }
}
