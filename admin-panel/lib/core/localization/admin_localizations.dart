import 'package:flutter/material.dart';

class AdminLocalizations {
  const AdminLocalizations(this.locale);

  final Locale locale;

  static const supportedLocales = [
    Locale('fa'),
    Locale('en'),
  ];

  static const LocalizationsDelegate<AdminLocalizations> delegate =
      _AdminLocalizationsDelegate();

  static AdminLocalizations of(BuildContext context) {
    return Localizations.of<AdminLocalizations>(
      context,
      AdminLocalizations,
    )!;
  }

  bool get isFa => locale.languageCode == 'fa';

  String get appName => isFa ? 'پنل ادمین فارم نت' : 'Farm Net Admin';
  String get dashboard => isFa ? 'داشبورد' : 'Dashboard';
  String get login => isFa ? 'ورود ادمین' : 'Admin Login';
  String get forbidden => isFa ? 'دسترسی غیرمجاز' : 'Forbidden';
  String get users => isFa ? 'کاربران' : 'Users';
  String get shops => isFa ? 'فروشگاه‌ها' : 'Shops';
  String get products => isFa ? 'محصولات' : 'Products';
  String get finance => isFa ? 'مالی' : 'Finance';
  String get settings => isFa ? 'تنظیمات' : 'Settings';
  String get loading => isFa ? 'در حال بارگذاری...' : 'Loading...';
  String get empty => isFa ? 'موردی برای نمایش وجود ندارد' : 'Nothing to show';
  String get retry => isFa ? 'تلاش دوباره' : 'Retry';
}

class _AdminLocalizationsDelegate
    extends LocalizationsDelegate<AdminLocalizations> {
  const _AdminLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['fa', 'en'].contains(locale.languageCode);
  }

  @override
  Future<AdminLocalizations> load(Locale locale) async {
    return AdminLocalizations(locale);
  }

  @override
  bool shouldReload(_AdminLocalizationsDelegate old) => false;
}
