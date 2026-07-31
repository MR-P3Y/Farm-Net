import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../state/auth_controller.dart';

class AuthenticatedRouteGuard extends ConsumerStatefulWidget {
  const AuthenticatedRouteGuard({required this.child, super.key});

  final Widget child;

  @override
  ConsumerState<AuthenticatedRouteGuard> createState() => _State();
}

class _State extends ConsumerState<AuthenticatedRouteGuard> {
  bool _requestedSession = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_requestedSession) return;
    _requestedSession = true;
    final auth = ref.read(authControllerProvider);
    if (auth.isLoading) {
      Future.microtask(
        () => ref.read(authControllerProvider.notifier).loadCurrentUser(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    if (auth.isLoading) {
      return const Scaffold(body: FarmLoadingView());
    }
    if (!auth.isAuthenticated || auth.user == null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.lock_outline, size: 52),
                const SizedBox(height: 14),
                Text(
                  context.l10n.tr(
                    fa: 'برای مشاهده این بخش ابتدا وارد حساب خود شوید.',
                    en: 'Sign in to view this section.',
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 18),
                FilledButton(
                  onPressed: () => context.go('/'),
                  child: Text(context.l10n.login),
                ),
              ],
            ),
          ),
        ),
      );
    }
    return widget.child;
  }
}
