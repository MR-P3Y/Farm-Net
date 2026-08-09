import 'package:farm_net/core/theme/theme_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  test('explicit light and dark choices are persisted', () async {
    SharedPreferences.setMockInitialValues({});
    final controller = ThemeController();

    await controller.setThemeMode(ThemeMode.dark);
    expect(controller.state, ThemeMode.dark);
    expect(
      (await SharedPreferences.getInstance()).getString('app_theme_mode'),
      'dark',
    );

    await controller.setThemeMode(ThemeMode.light);
    expect(controller.state, ThemeMode.light);
    expect(
      (await SharedPreferences.getInstance()).getString('app_theme_mode'),
      'light',
    );
  });
}
