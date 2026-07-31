import 'package:flutter/material.dart';

class AppTypography {
  const AppTypography._();

  static const irYekan = 'IRYekan';
  static const ptSans = 'PTSans';

  static String primaryFamily(Locale locale) {
    return locale.languageCode == 'fa' ? irYekan : ptSans;
  }

  static List<String> fallbackFamilies(Locale locale) {
    return locale.languageCode == 'fa' ? const [ptSans] : const [irYekan];
  }
}
