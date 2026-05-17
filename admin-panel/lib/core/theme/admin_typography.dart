import 'package:flutter/material.dart';

class AdminTypography {
  const AdminTypography._();

  static const iranianSans = 'IranianSans';
  static const ptSans = 'PTSans';

  static String primaryFamily(Locale locale) {
    return locale.languageCode == 'fa' ? iranianSans : ptSans;
  }

  static List<String> fallbackFamilies(Locale locale) {
    return locale.languageCode == 'fa'
        ? const [ptSans]
        : const [iranianSans];
  }
}
