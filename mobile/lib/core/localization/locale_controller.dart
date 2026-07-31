import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

final localeControllerProvider =
    StateNotifierProvider<LocaleController, Locale>(
      (ref) => LocaleController(),
    );

class LocaleController extends StateNotifier<Locale> {
  LocaleController() : super(const Locale('fa')) {
    _restore();
  }

  static const _storageKey = 'app_locale';

  Future<void> _restore() async {
    final code = (await SharedPreferences.getInstance()).getString(_storageKey);
    if (code == 'fa' || code == 'en') {
      state = Locale(code!);
    }
  }

  Future<void> setLocale(Locale locale) async {
    if (locale.languageCode != 'fa' && locale.languageCode != 'en') return;
    state = locale;
    await (await SharedPreferences.getInstance()).setString(
      _storageKey,
      locale.languageCode,
    );
  }

  Future<void> toggle() async {
    await setLocale(
      state.languageCode == 'fa' ? const Locale('en') : const Locale('fa'),
    );
  }
}
