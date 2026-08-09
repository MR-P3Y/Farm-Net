import 'package:flutter/material.dart';
import 'package:shamsi_date/shamsi_date.dart';
import 'package:intl/intl.dart' show DateFormat;

import 'digits.dart';

const _jalaliMonthNames = <String>[
  'فروردین',
  'اردیبهشت',
  'خرداد',
  'تیر',
  'مرداد',
  'شهریور',
  'مهر',
  'آبان',
  'آذر',
  'دی',
  'بهمن',
  'اسفند',
];

const _jalaliWeekdayNames = <String>[
  'شنبه',
  'یکشنبه',
  'دوشنبه',
  'سه‌شنبه',
  'چهارشنبه',
  'پنجشنبه',
  'جمعه',
];

/// A single locale-aware entry point for every calendar date selection.
///
/// Persian UI uses a real Jalali calendar while the returned value remains a
/// Gregorian [DateTime], so API and database contracts stay unchanged.
Future<DateTime?> showLocalizedDatePicker({
  required BuildContext context,
  DateTime? initialDate,
  required DateTime firstDate,
  required DateTime lastDate,
  DateTime? currentDate,
  SelectableDayPredicate? selectableDayPredicate,
  String? helpText,
  String? cancelText,
  String? confirmText,
  DatePickerEntryMode initialEntryMode = DatePickerEntryMode.calendar,
  DatePickerMode initialDatePickerMode = DatePickerMode.day,
}) {
  final locale = Localizations.localeOf(context);
  if (locale.languageCode != 'fa') {
    return showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: firstDate,
      lastDate: lastDate,
      currentDate: currentDate,
      selectableDayPredicate: selectableDayPredicate,
      helpText: helpText,
      cancelText: cancelText,
      confirmText: confirmText,
      initialEntryMode: initialEntryMode,
      initialDatePickerMode: initialDatePickerMode,
      locale: locale,
    );
  }

  const delegate = JalaliCalendarDelegate();
  final jalaliInitial =
      initialDate == null ? null : delegate.toCalendarDate(initialDate);
  final jalaliFirst = delegate.toCalendarDate(firstDate);
  final jalaliLast = delegate.toCalendarDate(lastDate);
  final jalaliCurrent = delegate.toCalendarDate(currentDate ?? DateTime.now());

  return showDatePicker(
    context: context,
    initialDate: jalaliInitial,
    firstDate: jalaliFirst,
    lastDate: jalaliLast,
    currentDate: jalaliCurrent,
    selectableDayPredicate:
        selectableDayPredicate == null
            ? null
            : (date) => selectableDayPredicate(delegate.toGregorianDate(date)),
    helpText: helpText ?? 'انتخاب تاریخ',
    cancelText: cancelText ?? 'لغو',
    confirmText: confirmText ?? 'تأیید',
    initialEntryMode: initialEntryMode,
    initialDatePickerMode: initialDatePickerMode,
    locale: const Locale('fa'),
    textDirection: TextDirection.rtl,
    calendarDelegate: delegate,
  ).then((date) => date == null ? null : delegate.toGregorianDate(date));
}

/// Jalali calendar implementation for Flutter's standard Material picker.
///
/// Flutter's picker requires [DateTime] values, so Jalali components are held
/// in a date-only proxy while the dialog is open. Public callers always pass
/// and receive ordinary Gregorian [DateTime] values through
/// [showLocalizedDatePicker].
class JalaliCalendarDelegate extends CalendarDelegate<DateTime> {
  const JalaliCalendarDelegate();

  DateTime toCalendarDate(DateTime date) {
    final jalali = Jalali.fromDateTime(date);
    return DateTime(jalali.year, jalali.month, jalali.day);
  }

  DateTime toGregorianDate(DateTime date) =>
      Jalali(date.year, date.month, date.day).toDateTime();

  @override
  DateTime now() => toCalendarDate(DateTime.now());

  @override
  DateTime dateOnly(DateTime date) => DateTime(date.year, date.month, date.day);

  @override
  int monthDelta(DateTime startDate, DateTime endDate) =>
      (endDate.year - startDate.year) * 12 + endDate.month - startDate.month;

  @override
  DateTime addMonthsToMonthDate(DateTime monthDate, int monthsToAdd) {
    final monthIndex = monthDate.year * 12 + monthDate.month - 1 + monthsToAdd;
    return DateTime(monthIndex ~/ 12, monthIndex % 12 + 1);
  }

  @override
  DateTime addDaysToDate(DateTime date, int days) =>
      toCalendarDate(toGregorianDate(date).add(Duration(days: days)));

  @override
  int firstDayOffset(
    int year,
    int month,
    MaterialLocalizations localizations,
  ) => Jalali(year, month).weekDay - 1;

  @override
  int getDaysInMonth(int year, int month) => Jalali(year, month).monthLength;

  @override
  DateTime getMonth(int year, int month) => DateTime(year, month);

  @override
  DateTime getDay(int year, int month, int day) => DateTime(year, month, day);

  @override
  String formatMonthYear(DateTime date, MaterialLocalizations localizations) =>
      '${_monthName(date.month)} ${toPersianDigits(date.year)}';

  @override
  String formatYear(int year, MaterialLocalizations localizations) =>
      toPersianDigits(year);

  @override
  String formatMediumDate(DateTime date, MaterialLocalizations localizations) =>
      '${_weekdayName(date)} ${toPersianDigits(date.day)} ${_monthName(date.month)}';

  @override
  String formatShortMonthDay(
    DateTime date,
    MaterialLocalizations localizations,
  ) => '${toPersianDigits(date.day)} ${_monthName(date.month)}';

  @override
  String formatShortDate(DateTime date, MaterialLocalizations localizations) =>
      formatCompactDate(date, localizations);

  @override
  String formatFullDate(DateTime date, MaterialLocalizations localizations) =>
      '${_weekdayName(date)} ${toPersianDigits(date.day)} ${_monthName(date.month)} ${toPersianDigits(date.year)}';

  @override
  String formatCompactDate(
    DateTime date,
    MaterialLocalizations localizations,
  ) => toPersianDigits(
    '${date.year}/${date.month.toString().padLeft(2, '0')}/${date.day.toString().padLeft(2, '0')}',
  );

  @override
  DateTime? parseCompactDate(
    String? inputString,
    MaterialLocalizations localizations,
  ) {
    if (inputString == null || inputString.trim().isEmpty) return null;
    final normalized = toEnglishDigits(
      inputString.trim().replaceAll('٫', '/').replaceAll('٬', ''),
    );
    final parts = normalized.split(RegExp(r'[/\-.]'));
    if (parts.length != 3) return null;
    final year = int.tryParse(parts[0]);
    final month = int.tryParse(parts[1]);
    final day = int.tryParse(parts[2]);
    if (year == null || month == null || day == null) return null;
    try {
      Jalali(year, month, day);
      return DateTime(year, month, day);
    } on Object {
      return null;
    }
  }

  @override
  String dateHelpText(MaterialLocalizations localizations) => 'سال/ماه/روز';

  String _monthName(int month) => _jalaliMonthNames[month - 1];

  String _weekdayName(DateTime date) {
    final weekday = Jalali(date.year, date.month, date.day).weekDay;
    return _jalaliWeekdayNames[weekday - 1];
  }
}

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
