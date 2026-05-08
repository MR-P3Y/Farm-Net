import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/auth/admin_auth_state.dart';
import '../../core/widgets/admin_loading_view.dart';
import 'admin_login_page.dart';
import 'state/admin_auth_controller.dart';

class AdminAuthGate extends ConsumerStatefulWidget {
  const AdminAuthGate({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<AdminAuthGate> createState() => _AdminAuthGateState();
}

class _AdminAuthGateState extends ConsumerState<AdminAuthGate> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminAuthControllerProvider).loadCurrentUser();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminAuthStateProvider);

    if (state.isLoading) {
      return const Scaffold(body: AdminLoadingView());
    }

    if (!state.isAuthenticated) {
      return const AdminLoginPage();
    }

    return widget.child;
  }
}
