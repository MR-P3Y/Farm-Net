import 'package:flutter/material.dart';

import 'admin_colors.dart';

class AdminTheme {
  const AdminTheme._();

  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AdminColors.primary,
        brightness: Brightness.light,
        error: AdminColors.error,
      ),
      scaffoldBackgroundColor: AdminColors.lightBackground,
      fontFamily: 'Roboto',
    );
  }

  static ThemeData get dark {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AdminColors.primary,
        brightness: Brightness.dark,
        error: AdminColors.error,
      ),
      scaffoldBackgroundColor: AdminColors.darkBackground,
      fontFamily: 'Roboto',
    );
  }
}
