import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/network/api_error.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/core/widgets/farm_back_button.dart';
import 'package:farm_net/core/widgets/farm_glass_card.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/presentation/auth_page_shell.dart';
import 'package:farm_net/features/auth/presentation/otp_request_screen.dart';
import 'package:farm_net/features/auth/presentation/otp_verify_screen.dart';
import 'package:farm_net/features/auth/presentation/registration_screen.dart';
import 'package:farm_net/features/geo/data/geo_models.dart';
import 'package:farm_net/features/geo/data/geo_api.dart';
import 'package:farm_net/features/geo/data/geo_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeGeoRepository implements GeoRepository {
  @override
  Future<List<GeoProvince>> getProvinces() async {
    return const [GeoProvince(id: 1, name: 'گلستان')];
  }

  @override
  Future<List<GeoCounty>> getCounties({required int provinceId}) async {
    return [GeoCounty(id: 2, provinceId: provinceId, name: 'گنبدکاووس')];
  }

  @override
  Future<List<GeoCity>> getCities({
    int? provinceId,
    int? countyId,
    String? q,
  }) async {
    return [
      GeoCity(
        id: 3,
        provinceId: provinceId,
        countyId: countyId,
        name: 'گنبدکاووس',
      ),
    ];
  }
}

class _TransientGeoRepository extends _FakeGeoRepository {
  int provinceCalls = 0;

  @override
  Future<List<GeoProvince>> getProvinces() async {
    provinceCalls += 1;
    if (provinceCalls == 1) {
      throw const GeoApiException(
        ApiError(code: 'NETWORK_ERROR', message: 'temporary network error'),
      );
    }
    return super.getProvinces();
  }
}

class _UnavailableGeoRepository extends _FakeGeoRepository {
  int provinceCalls = 0;

  @override
  Future<List<GeoProvince>> getProvinces() async {
    provinceCalls += 1;
    throw const GeoApiException(
      ApiError(code: 'NETWORK_ERROR', message: 'network unavailable'),
    );
  }
}

Widget _app({
  Locale locale = const Locale('fa'),
  Widget home = const RegistrationScreen(),
  GeoRepository? geoRepository,
}) {
  return ProviderScope(
    overrides: [
      geoRepositoryProvider.overrideWithValue(
        geoRepository ?? _FakeGeoRepository(),
      ),
    ],
    child: ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      splitScreenMode: true,
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
            home: home,
          ),
    ),
  );
}

void main() {
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  test('registration input serializes the atomic profile contract', () {
    const input = EmailRegistrationInput(
      email: 'farmer@example.com',
      password: 'strong-password',
      firstName: 'علی',
      lastName: 'کشاورز',
      nationalId: '1234567890',
      provinceId: 1,
      countyId: 2,
      address: 'نشانی',
    );

    final json = input.toJson();

    expect(json['first_name'], 'علی');
    expect(json['national_id'], '1234567890');
    expect(json['province_id'], 1);
    expect(json['county_id'], 2);
    expect(json['address'], 'نشانی');
    expect(json, isNot(contains('city_id')));
    expect(json, isNot(contains('postal_code')));
  });

  testWidgets('registration validates account fields before advancing', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 900);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    expect(find.text('اطلاعات حساب'), findsOneWidget);
    expect(find.text('مرحله ۱ از ۳'), findsOneWidget);

    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pump();
    expect(find.text('ایمیل را وارد کنید'), findsOneWidget);

    final fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'farmer@example.com');
    await tester.enterText(fields.at(1), 'strong-password');
    await tester.enterText(fields.at(2), 'strong-password');
    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    expect(find.text('مشخصات هویتی'), findsOneWidget);
    expect(find.text('مرحله ۲ از ۳'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('registration shell supports English', (tester) async {
    await tester.pumpWidget(_app(locale: const Locale('en')));
    await tester.pumpAndSettle();

    expect(find.text('Create Farm Net account'), findsOneWidget);
    expect(find.text('Step 1 of 3'), findsOneWidget);
    expect(find.text('Next step'), findsOneWidget);
  });

  testWidgets('location loading retries one transient failure automatically', (
    tester,
  ) async {
    final repository = _TransientGeoRepository();

    await tester.pumpWidget(_app(geoRepository: repository));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 700));
    await tester.pumpAndSettle();

    expect(repository.provinceCalls, 2);
    expect(find.textContaining('ارتباط با سرور مناطق'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('location loading explains a persistent network failure', (
    tester,
  ) async {
    final repository = _UnavailableGeoRepository();
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 1000);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app(geoRepository: repository));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 700));
    await tester.pumpAndSettle();

    expect(repository.provinceCalls, 2);
    var fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'farmer@example.com');
    await tester.enterText(fields.at(1), 'Strong@Password123');
    await tester.enterText(fields.at(2), 'Strong@Password123');
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'علی');
    await tester.enterText(fields.at(1), 'کشاورز');
    await tester.enterText(fields.at(3), '۱۲۳۴۵۶۷۸۹۰');
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    expect(
      find.text('ارتباط با سرور مناطق برقرار نشد. اتصال را بررسی کنید.'),
      findsOneWidget,
    );
    expect(find.text('تلاش دوباره'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('registration actions remain visible on narrow and wide sizes', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 844);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app());
    await tester.pump(const Duration(milliseconds: 300));

    final primary = find.byKey(const Key('registration-primary-action'));
    final secondary = find.byKey(const Key('registration-secondary-action'));
    final narrowPrimaryRect = tester.getRect(primary);
    final narrowSecondaryRect = tester.getRect(secondary);
    expect(find.text('بازگشت به ورود'), findsOneWidget);
    expect(narrowPrimaryRect.width, greaterThan(300));
    expect(narrowSecondaryRect.width, greaterThan(300));
    expect(narrowSecondaryRect.top, greaterThan(narrowPrimaryRect.bottom));
    expect(tester.takeException(), isNull);

    tester.view.physicalSize = const Size(1000, 900);
    await tester.pumpWidget(_app());
    await tester.pump(const Duration(milliseconds: 300));

    final widePrimaryRect = tester.getRect(primary);
    final wideSecondaryRect = tester.getRect(secondary);
    expect(widePrimaryRect.width, greaterThan(380));
    expect(wideSecondaryRect.width, greaterThan(380));
    expect(wideSecondaryRect.top, greaterThan(widePrimaryRect.bottom));
    expect(tester.takeException(), isNull);
  });

  testWidgets('registration actions float in a separate bottom panel', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 900);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    final formCard = find.byKey(const Key('registration-form-card'));
    final actionPanel = find.byKey(const Key('registration-action-panel'));
    final primary = find.byKey(const Key('registration-primary-action'));
    final layoutStack = find.byKey(const Key('registration-layout-stack'));
    final background = find.byKey(const Key('registration-background-image'));

    expect(formCard, findsOneWidget);
    expect(actionPanel, findsOneWidget);
    expect(find.byType(AuthPageShell), findsOneWidget);
    expect(find.descendant(of: formCard, matching: primary), findsNothing);
    expect(find.descendant(of: actionPanel, matching: primary), findsOneWidget);
    expect(
      find.descendant(of: formCard, matching: find.byType(FarmBackButton)),
      findsOneWidget,
    );
    expect(tester.widget<FarmGlassCard>(formCard).opacity, .1);
    expect(
      tester.widget<Scaffold>(find.byType(Scaffold)).resizeToAvoidBottomInset,
      isTrue,
    );
    expect(tester.getRect(background), tester.getRect(layoutStack));
    final keyboardInset =
        MediaQuery.viewInsetsOf(tester.element(layoutStack)).bottom;
    final availableBodyBottom = tester.getRect(layoutStack).bottom;
    final panelBottom = tester.getRect(actionPanel).bottom;
    expect(panelBottom, lessThanOrEqualTo(availableBodyBottom));
    expect(
      availableBodyBottom - panelBottom,
      inInclusiveRange(keyboardInset, keyboardInset + 40),
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('identity back action is not truncated on medium phone widths', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(560, 1000);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    final fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'farmer@example.com');
    await tester.enterText(fields.at(1), 'strong-password');
    await tester.enterText(fields.at(2), 'strong-password');
    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    final primary = find.byKey(const Key('registration-primary-action'));
    final secondary = find.byKey(const Key('registration-secondary-action'));
    await tester.ensureVisible(secondary);
    await tester.pumpAndSettle();

    expect(find.text('بازگشت'), findsOneWidget);
    expect(tester.getRect(secondary).width, greaterThan(300));
    expect(
      tester.getRect(secondary).top,
      greaterThan(tester.getRect(primary).bottom),
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('mobile OTP screens use the shared back button', (tester) async {
    await tester.pumpWidget(_app(home: const OtpRequestScreen()));
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.byType(FarmBackButton), findsOneWidget);
    expect(find.byType(AuthPageShell), findsOneWidget);

    await tester.pumpWidget(
      _app(home: const OtpVerifyScreen(phone: '09123456789')),
    );
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.byType(FarmBackButton), findsOneWidget);
    expect(find.byType(AuthPageShell), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('password strength reacts and National ID stays at ten digits', (
    tester,
  ) async {
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    final accountFields = find.byType(TextFormField);
    await tester.enterText(accountFields.at(0), 'farmer@example.com');
    await tester.enterText(accountFields.at(1), 'Strong@Password123');
    await tester.enterText(accountFields.at(2), 'Strong@Password123');
    expect(find.text('قوی'), findsOneWidget);

    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    final identityFields = find.byType(TextFormField);
    await tester.enterText(identityFields.at(3), '۱۲۳۴۵۶۷۸۹۰۱۲۳');
    final nationalIdField = tester.widget<TextFormField>(identityFields.at(3));
    expect(nationalIdField.controller?.text, '۱۲۳۴۵۶۷۸۹۰');
    expect(find.byIcon(Icons.privacy_tip_outlined), findsOneWidget);
  });

  testWidgets('province selection opens a searchable location sheet', (
    tester,
  ) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 900);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();
    var fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'farmer@example.com');
    await tester.enterText(fields.at(1), 'Strong@Password123');
    await tester.enterText(fields.at(2), 'Strong@Password123');
    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    fields = find.byType(TextFormField);
    await tester.enterText(fields.at(0), 'علی');
    await tester.enterText(fields.at(1), 'کشاورز');
    await tester.enterText(fields.at(3), '۱۲۳۴۵۶۷۸۹۰');
    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    expect(find.text('استان'), findsOneWidget);
    expect(find.text('انتخاب استان'), findsOneWidget);
    expect(
      tester.getRect(find.text('استان')).bottom,
      lessThan(tester.getRect(find.text('انتخاب استان')).top),
    );
    await tester.ensureVisible(find.text('انتخاب استان'));
    await tester.tap(find.text('انتخاب استان'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('registration-geo-search')), findsOneWidget);
    await tester.enterText(
      find.byKey(const Key('registration-geo-search')),
      'گل',
    );
    await tester.pump();
    expect(find.text('گلستان'), findsOneWidget);
    await tester.tap(find.text('گلستان'));
    await tester.pumpAndSettle();
    expect(find.text('گلستان'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('secure draft restores profile fields but never a password', (
    tester,
  ) async {
    FlutterSecureStorage.setMockInitialValues({
      'farmnet_registration_draft_v1':
          '{"email":"saved@example.com","first_name":"علی","national_id":"1234567890"}',
    });

    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    final fields = find.byType(TextFormField);
    expect(
      tester.widget<TextFormField>(fields.at(0)).controller?.text,
      'saved@example.com',
    );
    expect(
      tester.widget<TextFormField>(fields.at(1)).controller?.text,
      isEmpty,
    );
    expect(
      tester.widget<TextFormField>(fields.at(2)).controller?.text,
      isEmpty,
    );
  });

  testWidgets('final step shows a masked review before creating the account', (
    tester,
  ) async {
    FlutterSecureStorage.setMockInitialValues({
      'farmnet_registration_draft_v1':
          '{"email":"review@example.com","first_name":"علی","last_name":"کشاورز","national_id":"1234567890","province_id":1,"county_id":2,"city_id":3,"address":"نشانی آزمایشی"}',
    });
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 1100);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);

    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();
    final fields = find.byType(TextFormField);
    await tester.enterText(fields.at(1), 'Strong@Password123');
    await tester.enterText(fields.at(2), 'Strong@Password123');
    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('مرحله بعد'));
    await tester.tap(find.text('مرحله بعد'));
    await tester.pumpAndSettle();
    expect(find.text('گلستان'), findsOneWidget);
    expect(find.text('گنبدکاووس'), findsNWidgets(2));

    await tester.ensureVisible(find.text('مرور اطلاعات'));
    await tester.tap(find.text('مرور اطلاعات'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('registration-review-sheet')), findsOneWidget);
    expect(find.text('مرور اطلاعات ثبت‌نام'), findsOneWidget);
    expect(find.text('••••••7890'), findsOneWidget);
    expect(
      find.byKey(const Key('registration-review-confirm')),
      findsOneWidget,
    );
    await tester.tap(find.text('ویرایش'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('registration-review-sheet')), findsNothing);
    expect(tester.takeException(), isNull);
  });
}
