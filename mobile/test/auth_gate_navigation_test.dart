import 'package:farm_net/features/auth/data/auth_api.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/data/auth_repository.dart';
import 'package:farm_net/features/auth/presentation/auth_gate.dart';
import 'package:farm_net/features/auth/state/auth_controller.dart';
import 'package:farm_net/features/auth/state/auth_state.dart';
import 'package:farm_net/core/storage/token_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _AuthenticatedController extends AuthController {
  _AuthenticatedController()
    : super(
        repository: AuthRepository(
          api: AuthApi(),
          tokenStorage: TokenStorage(),
        ),
      ) {
    state = const AuthState(
      isLoading: false,
      isAuthenticated: true,
      user: AuthUser(
        id: 1,
        status: 'active',
        isEmailVerified: true,
        isPhoneVerified: false,
      ),
    );
  }

  @override
  Future<void> loadCurrentUser() async {}
}

void main() {
  testWidgets('authenticated gate enters the routed app shell destination', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(path: '/', builder: (_, _) => const AuthGate()),
        GoRoute(
          path: '/home',
          builder: (_, _) => const Scaffold(body: Text('ROUTED-HOME')),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            (ref) => _AuthenticatedController(),
          ),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('ROUTED-HOME'), findsOneWidget);
    expect(router.routeInformationProvider.value.uri.path, '/home');
  });
}
