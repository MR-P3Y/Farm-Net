import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_typography.dart';

class AppTheme {
  const AppTheme._();

  static ThemeData light(Locale locale) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.light,
        error: AppColors.error,
      ),
      scaffoldBackgroundColor: AppColors.lightBackground,
      fontFamily: AppTypography.primaryFamily(locale),
      fontFamilyFallback: AppTypography.fallbackFamilies(locale),
    );
  }

  static ThemeData dark(Locale locale) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
        error: AppColors.error,
      ),
      scaffoldBackgroundColor: AppColors.darkBackground,
      fontFamily: AppTypography.primaryFamily(locale),
      fontFamilyFallback: AppTypography.fallbackFamilies(locale),
    );
  }
}
