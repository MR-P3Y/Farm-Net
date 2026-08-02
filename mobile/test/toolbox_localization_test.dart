import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/features/toolbox/data/toolbox_api.dart';
import 'package:farm_net/core/network/api_error.dart';
import 'package:farm_net/features/toolbox/presentation/toolbox_localization.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Locale locale, Widget child) => MaterialApp(
  locale: locale,
  supportedLocales: AppLocalizations.supportedLocales,
  localizationsDelegates: const [
    AppLocalizations.delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  home: Scaffold(body: child),
);

void main() {
  testWidgets('toolbox units and values are fully Persian in fa locale', (
    tester,
  ) async {
    String? unit;
    String? value;
    await tester.pumpWidget(
      _app(
        const Locale('fa'),
        Builder(
          builder: (context) {
            unit = localizeToolboxUnit(context, 'kg/ha');
            value = formatToolboxValue(context, 12.5, 'L/min');
            return const SizedBox();
          },
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(unit, 'کیلوگرم/هکتار');
    expect(value, '۱۲.۵۰ لیتر/دقیقه');
  });

  testWidgets('toolbox units remain English in en locale', (tester) async {
    String? value;
    await tester.pumpWidget(
      _app(
        const Locale('en'),
        Builder(
          builder: (context) {
            value = formatToolboxValue(context, 10, 'kg');
            return const SizedBox();
          },
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(value, '10 kg');
  });

  testWidgets('not found is explained as server version, not offline', (
    tester,
  ) async {
    String? message;
    await tester.pumpWidget(
      _app(
        const Locale('fa'),
        Builder(
          builder: (context) {
            message = localizeToolboxError(
              context,
              const ToolboxApiException(
                ApiError(code: 'NOT_FOUND', message: 'Not Found'),
                statusCode: 404,
              ),
            );
            return const SizedBox();
          },
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(message, contains('نسخهٔ درحال‌اجرای سرور'));
    expect(message, isNot(contains('آفلاین')));
  });
}
