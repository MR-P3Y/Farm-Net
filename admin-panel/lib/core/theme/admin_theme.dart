import 'package:flutter/material.dart';

import 'admin_colors.dart';
import 'admin_typography.dart';

class AdminTheme {
  const AdminTheme._();

  static ThemeData light(Locale locale) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AdminColors.primary,
        brightness: Brightness.light,
        error: AdminColors.error,
      ),
      scaffoldBackgroundColor: AdminColors.lightBackground,
      fontFamily: AdminTypography.primaryFamily(locale),
      fontFamilyFallback: AdminTypography.fallbackFamilies(locale),
    );
  }

  static ThemeData dark(Locale locale) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AdminColors.primary,
        brightness: Brightness.dark,
        error: AdminColors.error,
      ),
      scaffoldBackgroundColor: AdminColors.darkBackground,
      fontFamily: AdminTypography.primaryFamily(locale),
      fontFamilyFallback: AdminTypography.fallbackFamilies(locale),
    );
  }
}
