import 'package:shamsi_date/shamsi_date.dart';

import 'digits.dart';

String formatJalaliDate(
  DateTime date, {
  bool persianDigits = true,
}) {
  final jalali = Jalali.fromDateTime(date);

  final value = '${jalali.year}/${jalali.month.toString().padLeft(2, '0')}/${jalali.day.toString().padLeft(2, '0')}';

  return persianDigits ? toPersianDigits(value) : value;
}