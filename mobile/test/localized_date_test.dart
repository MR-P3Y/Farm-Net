import 'package:farm_net/core/utils/dates.dart';
import 'package:flutter/material.dart';
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
}
