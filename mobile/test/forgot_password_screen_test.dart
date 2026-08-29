import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/storage/token_storage.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/auth/data/auth_api.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/data/auth_repository.dart';
import 'package:farm_net/features/auth/presentation/auth_page_shell.dart';
import 'package:farm_net/features/auth/presentation/forgot_password_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthRepository extends AuthRepository {
  _FakeAuthRepository() : super(api: AuthApi(), tokenStorage: TokenStorage());

  String? requestedIdentifier;
  ({String identifier, String code, String password})? confirmation;

  @override
  Future<PasswordResetRequestResult> requestPasswordReset({
    required String identifier,
  }) async {
    requestedIdentifier = identifier;
    return const PasswordResetRequestResult(
      expiresInSeconds: 120,
      devCode: '111111',
    );
  }

  @override
  Future<int> confirmPasswordReset({
    required String identifier,
    required String code,
    required String newPassword,
  }) async {
    confirmation = (identifier: identifier, code: code, password: newPassword);
    return 2;
  }
}

Widget _app(_FakeAuthRepository repository) {
  const locale = Locale('fa');
  return ProviderScope(
    overrides: [authRepositoryProvider.overrideWithValue(repository)],
    child: ScreenUtilInit(
      designSize: const Size(390, 844),
      builder:
          (context, _) => MaterialApp(
            locale: locale,
            supportedLocales: AppLocalizations.supportedLocales,
            localizationsDelegates: const [
              AppLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            theme: AppTheme.light(locale),
            home: const ForgotPasswordScreen(),
          ),
    ),
  );
}

Finder _field(Key key) {
  return find.descendant(
    of: find.byKey(key),
    matching: find.byType(TextFormField),
  );
}

void main() {
  testWidgets('password reset completes the request and confirmation flow', (
    tester,
  ) async {
    final repository = _FakeAuthRepository();
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 900);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app(repository));
    await tester.pumpAndSettle();

    expect(find.byType(AuthPageShell), findsOneWidget);
    expect(
      tester.widget<Scaffold>(find.byType(Scaffold)).resizeToAvoidBottomInset,
      isTrue,
    );
    await tester.enterText(
      _field(const Key('password-reset-identifier')),
      'farmer@example.com',
    );
    await tester.tap(find.byKey(const Key('password-reset-request-action')));
    await tester.pumpAndSettle();

    expect(repository.requestedIdentifier, 'farmer@example.com');
    expect(find.text('کد محیط توسعه: 111111'), findsOneWidget);

    await tester.enterText(_field(const Key('password-reset-code')), '111111');
    await tester.enterText(
      _field(const Key('password-reset-new-password')),
      'new-password-123',
    );
    await tester.enterText(
      _field(const Key('password-reset-confirm-password')),
      'new-password-123',
    );
    await tester.ensureVisible(
      find.byKey(const Key('password-reset-confirm-action')),
    );
    await tester.tap(find.byKey(const Key('password-reset-confirm-action')));
    await tester.pumpAndSettle();

    expect(repository.confirmation?.identifier, 'farmer@example.com');
    expect(repository.confirmation?.code, '111111');
    expect(repository.confirmation?.password, 'new-password-123');
    expect(find.text('رمز عبور تغییر کرد'), findsOneWidget);
    expect(
      find.byKey(const Key('password-reset-back-to-login')),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });
}
