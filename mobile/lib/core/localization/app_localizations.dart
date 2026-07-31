import 'package:flutter/material.dart';

class AppLocalizations {
  const AppLocalizations(this.locale);

  final Locale locale;

  static const supportedLocales = [Locale('fa'), Locale('en')];

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations) ??
        AppLocalizations(
          Localizations.maybeLocaleOf(context) ?? const Locale('fa'),
        );
  }

  bool get isFa => locale.languageCode == 'fa';

  String tr({required String fa, required String en}) => isFa ? fa : en;

  String get appName => isFa ? 'فارم نت' : 'Farm Net';
  String get welcome => isFa ? 'به فارم نت خوش آمدید' : 'Welcome to Farm Net';
  String get home => isFa ? 'خانه' : 'Home';
  String get discover => isFa ? 'کشف' : 'Discover';
  String get barzegar => isFa ? 'برزگر' : 'Barzegar';
  String get myActivity => isFa ? 'فعالیت‌های من' : 'My activity';
  String get allServices => isFa ? 'همه خدمات' : 'All services';
  String get consultants => isFa ? 'مشاوران' : 'Consultants';
  String get services => isFa ? 'خدمات' : 'Services';
  String get weather => isFa ? 'هواشناسی' : 'Weather';
  String get social => isFa ? 'جامعه کشاورزان' : 'Community';
  String get marketplace => isFa ? 'بازار' : 'Marketplace';
  String get rentals => isFa ? 'اجاره تجهیزات' : 'Equipment rental';
  String get farms => isFa ? 'مزارع من' : 'My farms';
  String get back => isFa ? 'بازگشت' : 'Back';
  String get close => isFa ? 'بستن' : 'Close';
  String get loading => isFa ? 'در حال بارگذاری...' : 'Loading...';
  String get search => isFa ? 'جست‌وجو...' : 'Search...';
  String get retry => isFa ? 'تلاش دوباره' : 'Retry';
  String get empty => isFa ? 'موردی برای نمایش وجود ندارد' : 'Nothing to show';
  String get error => isFa ? 'خطایی رخ داد' : 'Something went wrong';
  String get offline =>
      isFa ? 'اتصال اینترنت را بررسی کنید' : 'Check your internet connection';
  String get forbidden => isFa ? 'دسترسی غیرمجاز است' : 'Access denied';
  String get notFound => isFa ? 'مورد پیدا نشد' : 'Not found';

  // Auth
  String get login => isFa ? 'ورود به سیستم' : 'Login';
  String get register => isFa ? 'ثبت‌نام' : 'Register';
  String get emailOrUsername =>
      isFa ? 'ایمیل یا نام کاربری' : 'Email or Username';
  String get password => isFa ? 'رمز عبور' : 'Password';
  String get loginWithMobile => isFa ? 'ورود با موبایل' : 'Login with Mobile';
  String get mobileNumber => isFa ? 'شماره موبایل' : 'Mobile Number';
  String get getOtpCode => isFa ? 'دریافت کد تایید' : 'Get Verification Code';
  String get verifyCode => isFa ? 'تأیید کد' : 'Verify Code';
  String get enterOtpSentTo =>
      isFa
          ? 'کد ارسال‌شده برای $mobileNumber را وارد کنید'
          : 'Enter the code sent to $mobileNumber';
  String get verifyAndLogin => isFa ? 'تأیید و ورود' : 'Verify and Login';
  String get verificationCode => isFa ? 'کد تأیید' : 'Verification Code';

  // Profile
  String get profile => isFa ? 'پروفایل' : 'Profile';
  String get settings => isFa ? 'تنظیمات' : 'Settings';
  String get darkMode => isFa ? 'حالت تیره' : 'Dark Mode';
  String get language => isFa ? 'زبان' : 'Language';
  String get logout => isFa ? 'خروج از حساب' : 'Logout';
}

extension AppLocalizationsX on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
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
