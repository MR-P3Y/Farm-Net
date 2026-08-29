import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/storage/token_storage.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/auth/data/auth_api.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/data/auth_repository.dart';
import 'package:farm_net/features/auth/presentation/account_security_screen.dart';
import 'package:farm_net/features/auth/state/account_security_controller.dart';
import 'package:farm_net/features/auth/state/auth_controller.dart';
import 'package:farm_net/features/auth/state/auth_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_test/flutter_test.dart';

const _emailUser = AuthUser(
  id: 7,
  email: 'farmer@example.com',
  status: 'active',
  isEmailVerified: true,
  isPhoneVerified: false,
);

const _sessions = [
  AuthSessionModel(
    id: 11,
    status: 'active',
    isCurrent: true,
    createdAt: '2026-08-20T10:00:00',
    lastSeenAt: '2026-08-23T12:30:00',
    ipAddress: '127.0.0.1',
    userAgent: 'Mozilla/5.0 Chrome/140.0',
  ),
  AuthSessionModel(
    id: 12,
    status: 'active',
    isCurrent: false,
    createdAt: '2026-08-21T10:00:00',
    lastSeenAt: '2026-08-22T08:00:00',
    ipAddress: '10.0.2.2',
    userAgent: 'FarmNet Android',
  ),
];

void main() {
  testWidgets('security screen identifies current and remote sessions', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('en'),
        securityState: const AccountSecurityState(sessions: _sessions),
        user: _emailUser,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Account security'), findsOneWidget);
    expect(find.text('Change password'), findsWidgets);
    expect(find.text('Chrome'), findsOneWidget);
    expect(find.text('Android'), findsOneWidget);
    expect(find.text('This device'), findsOneWidget);
    expect(find.text('Close all other sessions'), findsOneWidget);
  });

  testWidgets('OTP-only account does not show a fixed-password action', (
    tester,
  ) async {
    const phoneUser = AuthUser(
      id: 8,
      phone: '+989121234567',
      status: 'active',
      isEmailVerified: false,
      isPhoneVerified: true,
    );
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('fa'),
        securityState: const AccountSecurityState(sessions: _sessions),
        user: phoneUser,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('رمز یک‌بارمصرف وارد شده است'), findsOneWidget);
    expect(find.text('تغییر رمز عبور'), findsNothing);
  });
}

Widget _testApp({
  required Locale locale,
  required AccountSecurityState securityState,
  required AuthUser user,
}) {
  return ProviderScope(
    overrides: [
      accountSecurityControllerProvider.overrideWith(
        (ref) => _TestAccountSecurityController(securityState),
      ),
      authControllerProvider.overrideWith(
        (ref) => _TestAuthController(
          AuthState(isLoading: false, isAuthenticated: true, user: user),
        ),
      ),
    ],
    child: ScreenUtilInit(
      designSize: const Size(390, 844),
      builder:
          (context, _) => MaterialApp(
            locale: locale,
            theme: AppTheme.light(locale),
            darkTheme: AppTheme.dark(locale),
            supportedLocales: AppLocalizations.supportedLocales,
            localizationsDelegates: const [
              AppLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            home: const AccountSecurityScreen(),
          ),
    ),
  );
}

class _TestAccountSecurityController extends AccountSecurityController {
  _TestAccountSecurityController(AccountSecurityState initial)
    : super(
        repository: AuthRepository(
          api: AuthApi(),
          tokenStorage: TokenStorage(),
        ),
      ) {
    state = initial;
  }

  @override
  Future<void> load() async {}
}

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

  @override
  Future<void> loadCurrentUser() async {}
}
