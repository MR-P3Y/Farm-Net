import 'package:farm_net_admin/core/utils/dates.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Persian Admin dates use Jalali calendar and Persian digits', () {
    final value = DateTime(2025, 3, 20, 14, 5);

    expect(
      formatLocalizedAdminDate(value, locale: const Locale('fa')),
      '۱۴۰۳/۱۲/۳۰ ۱۴:۰۵',
    );
  });

  test('English Admin dates remain Gregorian with English digits', () {
    final value = DateTime(2025, 3, 20, 14, 5);

    expect(
      formatLocalizedAdminDate(value, locale: const Locale('en')),
      '2025-03-20 14:05',
    );
  });

  test('date formatter supports date-only and empty values', () {
    final value = DateTime(2025, 3, 20, 14, 5);

    expect(
      formatLocalizedAdminDate(
        value,
        locale: const Locale('fa'),
        showTime: false,
      ),
      '۱۴۰۳/۱۲/۳۰',
    );
    expect(formatLocalizedAdminDate(null, locale: const Locale('fa')), '-');
  });
}
