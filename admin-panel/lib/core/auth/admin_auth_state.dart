import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/data/admin_auth_models.dart';

final adminAuthStateProvider =
    StateNotifierProvider<AdminAuthStateController, AdminAuthState>(
      (ref) => AdminAuthStateController(),
    );

class AdminAuthState {
  const AdminAuthState({
    required this.isLoading,
    required this.isAuthenticated,
    this.user,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isAuthenticated;
  final AdminAuthUser? user;
  final String? errorMessage;

  Set<String> get permissions => user?.permissions.toSet() ?? {};

  bool hasPermission(String permission) {
    return permissions.contains(permission);
  }

  bool hasAnyPermission(List<String> items) {
    return items.any(permissions.contains);
  }

  factory AdminAuthState.initial() {
    return const AdminAuthState(isLoading: true, isAuthenticated: false);
  }

  AdminAuthState copyWith({
    bool? isLoading,
    bool? isAuthenticated,
    AdminAuthUser? user,
    String? errorMessage,
    bool clearError = false,
  }) {
    return AdminAuthState(
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      user: user ?? this.user,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }

  AdminAuthState unauthenticated() {
    return const AdminAuthState(isLoading: false, isAuthenticated: false);
  }
}

class AdminAuthStateController extends StateNotifier<AdminAuthState> {
  AdminAuthStateController() : super(AdminAuthState.initial());

  void setLoading() {
    state = state.copyWith(isLoading: true, clearError: true);
  }

  void setAuthenticated(AdminAuthUser user) {
    state = AdminAuthState(isLoading: false, isAuthenticated: true, user: user);
  }

  void setUnauthenticated() {
    state = state.unauthenticated();
  }

  void setError(String message) {
    state = AdminAuthState(
      isLoading: false,
      isAuthenticated: false,
      errorMessage: message,
    );
  }
}
