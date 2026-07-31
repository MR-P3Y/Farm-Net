import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_radius.dart';
import 'app_theme_extensions.dart';
import 'app_typography.dart';

class AppTheme {
  const AppTheme._();

  static ThemeData light(Locale locale) {
    return _build(
      locale: locale,
      brightness: Brightness.light,
      background: AppColors.lightBackground,
      glass: FarmGlassTheme(
        surface: Colors.white.withValues(alpha: 0.58),
        surfaceStrong: Colors.white.withValues(alpha: 0.82),
        border: Colors.white.withValues(alpha: 0.72),
        highlight: Colors.white.withValues(alpha: 0.92),
        shadow: const Color(0xFF173C25).withValues(alpha: 0.12),
        blur: 18,
      ),
    );
  }

  static ThemeData dark(Locale locale) {
    return _build(
      locale: locale,
      brightness: Brightness.dark,
      background: AppColors.darkBackground,
      glass: FarmGlassTheme(
        surface: const Color(0xFF183024).withValues(alpha: 0.48),
        surfaceStrong: const Color(0xFF1D382A).withValues(alpha: 0.76),
        border: Colors.white.withValues(alpha: 0.12),
        highlight: Colors.white.withValues(alpha: 0.18),
        shadow: Colors.black.withValues(alpha: 0.34),
        blur: 20,
      ),
    );
  }

  static ThemeData _build({
    required Locale locale,
    required Brightness brightness,
    required Color background,
    required FarmGlassTheme glass,
  }) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: brightness,
      error: AppColors.error,
    );
    final base = ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: background,
      fontFamily: AppTypography.primaryFamily(locale),
      fontFamilyFallback: AppTypography.fallbackFamilies(locale),
      extensions: [glass],
      visualDensity: VisualDensity.standard,
    );

    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(AppRadius.md),
    );
    return base.copyWith(
      textTheme: base.textTheme.apply(
        bodyColor: colorScheme.onSurface,
        displayColor: colorScheme.onSurface,
      ),
      appBarTheme: AppBarTheme(
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: colorScheme.onSurface,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: glass.surfaceStrong,
        shape: shape,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(48, 48),
          shape: shape,
          textStyle: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(48, 48),
          shape: shape,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: glass.surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: glass.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: glass.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: colorScheme.primary, width: 1.5),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        elevation: 0,
        backgroundColor: glass.surfaceStrong,
        indicatorColor: colorScheme.primaryContainer,
      ),
      dividerTheme: DividerThemeData(color: colorScheme.outlineVariant),
    );
  }
}
