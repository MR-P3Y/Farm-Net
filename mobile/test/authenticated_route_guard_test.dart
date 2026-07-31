import 'package:farm_net/core/storage/token_storage.dart';
import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/features/auth/data/auth_api.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/data/auth_repository.dart';
import 'package:farm_net/features/auth/presentation/authenticated_route_guard.dart';
import 'package:farm_net/features/auth/state/auth_controller.dart';
import 'package:farm_net/features/auth/state/auth_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

class _TestAuthController extends AuthController {
  _TestAuthController(AuthState initial)
    : super(
        repository: AuthRepository(
          api: AuthApi(),
          tokenStorage: TokenStorage(),
        ),
      ) {
    state = initial;
  }
}

void main() {
  testWidgets('guard hides private child from unauthenticated user', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            (ref) => _TestAuthController(
              const AuthState(isLoading: false, isAuthenticated: false),
            ),
          ),
        ],
        child: const MaterialApp(
          locale: Locale('fa'),
          supportedLocales: AppLocalizations.supportedLocales,
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          home: AuthenticatedRouteGuard(child: Text('PRIVATE-CONTENT')),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('PRIVATE-CONTENT'), findsNothing);
    expect(find.textContaining('ابتدا وارد حساب'), findsOneWidget);
  });

  testWidgets('guard renders private child for authenticated user', (
    tester,
  ) async {
    const user = AuthUser(
      id: 1,
      status: 'active',
      isEmailVerified: true,
      isPhoneVerified: true,
      roles: ['user'],
      permissions: [],
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            (ref) => _TestAuthController(
              const AuthState(
                isLoading: false,
                isAuthenticated: true,
                user: user,
              ),
            ),
          ),
        ],
        child: const MaterialApp(
          locale: Locale('fa'),
          supportedLocales: AppLocalizations.supportedLocales,
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          home: AuthenticatedRouteGuard(child: Text('PRIVATE-CONTENT')),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('PRIVATE-CONTENT'), findsOneWidget);
  });
}
