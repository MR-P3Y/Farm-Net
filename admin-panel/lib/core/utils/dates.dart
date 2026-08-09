import 'package:flutter/material.dart';
import 'package:shamsi_date/shamsi_date.dart';

/// Formats an API [DateTime] for the active Admin locale.
///
/// Persian UI uses the Solar Hijri calendar and Persian digits. English UI
/// remains Gregorian. The source value is never mutated or converted at API
/// boundaries; only its user-facing representation changes.
String formatAdminDate(
  BuildContext context,
  DateTime? value, {
  bool showTime = true,
}) => formatLocalizedAdminDate(
  value,
  locale: Localizations.localeOf(context),
  showTime: showTime,
);

String formatLocalizedAdminDate(
  DateTime? value, {
  required Locale locale,
  bool showTime = true,
}) {
  if (value == null) return '-';

  final local = value.toLocal();
  final time =
      '${local.hour.toString().padLeft(2, '0')}:'
      '${local.minute.toString().padLeft(2, '0')}';

  if (locale.languageCode == 'fa') {
    final jalali = Jalali.fromDateTime(local);
    final date =
        '${jalali.year}/'
        '${jalali.month.toString().padLeft(2, '0')}/'
        '${jalali.day.toString().padLeft(2, '0')}';
    return _toPersianDigits(showTime ? '$date $time' : date);
  }

  final date =
      '${local.year.toString().padLeft(4, '0')}-'
      '${local.month.toString().padLeft(2, '0')}-'
      '${local.day.toString().padLeft(2, '0')}';
  return showTime ? '$date $time' : date;
}

String _toPersianDigits(Object value) {
  const english = '0123456789';
  const persian = '۰۱۲۳۴۵۶۷۸۹';
  return value.toString().split('').map((character) {
    final index = english.indexOf(character);
    return index == -1 ? character : persian[index];
  }).join();
}
