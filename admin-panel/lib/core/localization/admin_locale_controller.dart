import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final adminLocaleControllerProvider =
    StateNotifierProvider<AdminLocaleController, Locale>(
  (ref) => AdminLocaleController(),
);

class AdminLocaleController extends StateNotifier<Locale> {
  AdminLocaleController() : super(const Locale('fa'));

  void setLocale(Locale locale) {
    state = locale;
  }

  void toggle() {
    state = state.languageCode == 'fa' ? const Locale('en') : const Locale('fa');
  }
}
