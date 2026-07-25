import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../localization/app_localizations.dart';

import 'digits.dart';

String formatToman(
  BuildContext context,
  num amount, {
  bool persianDigits = true,
  bool showCurrency = true,
}) {
  final l10n = AppLocalizations.of(context);
  final isFa = l10n.isFa;

  final formatter = NumberFormat.decimalPattern(isFa ? 'fa' : 'en');
  final formatted = formatter.format(amount);

  if (!showCurrency) return formatted;

  final currency = isFa ? 'تومان' : 'Toman';
  final result = isFa ? '$formatted $currency' : '$formatted $currency';

  return (isFa && persianDigits) ? toPersianDigits(result) : result;
}
