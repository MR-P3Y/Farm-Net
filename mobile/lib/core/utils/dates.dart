import 'package:flutter/material.dart';
import 'package:shamsi_date/shamsi_date.dart';
import 'package:intl/intl.dart';

import 'digits.dart';

String formatDate(
  BuildContext context,
  DateTime date, {
  bool persianDigits = true,
  bool showTime = false,
}) {
  final locale = Localizations.localeOf(context);
  final isFa = locale.languageCode == 'fa';

  if (isFa) {
    final jalali = Jalali.fromDateTime(date);
    final dateStr =
        '${jalali.year}/${jalali.month.toString().padLeft(2, '0')}/${jalali.day.toString().padLeft(2, '0')}';

    if (showTime) {
      final timeStr =
          '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
      final result = '$dateStr $timeStr';
      return persianDigits ? toPersianDigits(result) : result;
    }

    return persianDigits ? toPersianDigits(dateStr) : dateStr;
  } else {
    final format =
        showTime ? DateFormat.yMd('en').add_jm() : DateFormat.yMd('en');
    return format.format(date);
  }
}

String formatLocalizedDate(
  DateTime date, {
  required Locale locale,
  bool showTime = false,
  bool persianDigits = true,
}) {
  if (locale.languageCode == 'fa') {
    final jalali = Jalali.fromDateTime(date);
    final dateValue =
        '${jalali.year}/${jalali.month.toString().padLeft(2, '0')}/${jalali.day.toString().padLeft(2, '0')}';
    final value =
        showTime
            ? '$dateValue ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}'
            : dateValue;
    return persianDigits ? toPersianDigits(value) : value;
  }

  return (showTime ? DateFormat.yMd('en').add_jm() : DateFormat.yMd('en'))
      .format(date);
}

extension DateTimeX on DateTime {
  String format(
    BuildContext context, {
    bool showTime = false,
    bool persianDigits = true,
  }) {
    return formatDate(
      context,
      this,
      showTime: showTime,
      persianDigits: persianDigits,
    );
  }
}

String formatJalaliDate(DateTime date, {bool persianDigits = true}) {
  final jalali = Jalali.fromDateTime(date);

  final value =
      '${jalali.year}/${jalali.month.toString().padLeft(2, '0')}/${jalali.day.toString().padLeft(2, '0')}';

  return persianDigits ? toPersianDigits(value) : value;
}
