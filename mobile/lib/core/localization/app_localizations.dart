import 'package:flutter/material.dart';

class AppLocalizations {
  const AppLocalizations(this.locale);

  final Locale locale;

  static const supportedLocales = [
    Locale('fa'),
    Locale('en'),
  ];

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  bool get isFa => locale.languageCode == 'fa';

  String get appName => isFa ? 'فارم نت' : 'Farm Net';
  String get welcome => isFa ? 'به فارم نت خوش آمدید' : 'Welcome to Farm Net';
  String get home => isFa ? 'خانه' : 'Home';
  String get loading => isFa ? 'در حال بارگذاری...' : 'Loading...';
  String get retry => isFa ? 'تلاش دوباره' : 'Retry';
  String get empty => isFa ? 'موردی برای نمایش وجود ندارد' : 'Nothing to show';
  String get error => isFa ? 'خطایی رخ داد' : 'Something went wrong';
  String get forbidden => isFa ? 'دسترسی غیرمجاز است' : 'Access denied';
  String get notFound => isFa ? 'مورد پیدا نشد' : 'Not found';
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['fa', 'en'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
