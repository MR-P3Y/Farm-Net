import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../splash/splash_screen.dart';
import '../state/auth_controller.dart';
import 'login_screen.dart';

class AuthGate extends ConsumerStatefulWidget {
  const AuthGate({super.key});

  @override
  ConsumerState<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends ConsumerState<AuthGate> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(authControllerProvider.notifier).loadCurrentUser();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);

    if (state.isLoading) {
      return const SplashScreen();
    }

    if (state.isAuthenticated) {
      return const _AuthenticatedRedirect();
    }

    return const LoginScreen();
  }
}

class _AuthenticatedRedirect extends StatefulWidget {
  const _AuthenticatedRedirect();

  @override
  State<_AuthenticatedRedirect> createState() => _AuthenticatedRedirectState();
}

class _AuthenticatedRedirectState extends State<_AuthenticatedRedirect> {
  bool _scheduled = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_scheduled) return;
    _scheduled = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) context.go('/home');
    });
  }

  @override
  Widget build(BuildContext context) => const SplashScreen(compact: true);
}
