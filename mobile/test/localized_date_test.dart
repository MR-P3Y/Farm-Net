import 'package:farm_net/core/utils/dates.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

Future<void> main() async {
  await initializeDateFormatting('en');
  final date = DateTime(2025, 3, 20, 14, 5);

  test('Persian locale formats dates with the Jalali calendar', () {
    expect(formatLocalizedDate(date, locale: const Locale('fa')), '۱۴۰۳/۱۲/۳۰');
  });

  test('English locale formats dates with the Gregorian calendar', () {
    expect(formatLocalizedDate(date, locale: const Locale('en')), '3/20/2025');
  });

  testWidgets('API timestamps use Jalali in Persian UI', (tester) async {
    late String value;
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('fa'),
        supportedLocales: const [Locale('fa'), Locale('en')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        home: Builder(
          builder: (context) {
            value = formatApiDate(context, '2025-03-20T14:05:00Z');
            return const SizedBox();
          },
        ),
      ),
    );
    expect(value, '۱۴۰۳/۱۲/۳۰');
  });

  testWidgets('API timestamps remain Gregorian in English UI', (tester) async {
    late String value;
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('en'),
        supportedLocales: const [Locale('fa'), Locale('en')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        home: Builder(
          builder: (context) {
            value = formatApiDate(context, '2025-03-20T14:05:00Z');
            return const SizedBox();
          },
        ),
      ),
    );
    expect(value, '3/20/2025');
  });
}
