import 'package:intl/intl.dart';

import 'digits.dart';

String formatToman(
  num amount, {
  bool persianDigits = true,
  bool showCurrency = true,
}) {
  final formatter = NumberFormat.decimalPattern('en');
  final formatted = formatter.format(amount);
  final withCurrency = showCurrency ? '$formatted تومان' : formatted;

  return persianDigits ? toPersianDigits(withCurrency) : withCurrency;
}
