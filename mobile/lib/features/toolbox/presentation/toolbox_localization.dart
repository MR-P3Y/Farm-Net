import 'package:flutter/material.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/digits.dart';
import '../../../core/utils/money.dart';
import '../data/toolbox_api.dart';

String localizeToolboxDigits(BuildContext context, String value) =>
    context.l10n.isFa ? toPersianDigits(value) : value;

String localizeToolboxUnit(BuildContext context, String unit) {
  if (!context.l10n.isFa) return unit == 'TOMAN' ? 'Toman' : unit;
  const units = {
    'm²': 'مترمربع',
    'ha': 'هکتار',
    'm³': 'مترمکعب',
    'm': 'متر',
    'mm': 'میلی‌متر',
    'L': 'لیتر',
    'mL': 'میلی‌لیتر',
    'L/min': 'لیتر/دقیقه',
    'm³/h': 'مترمکعب/ساعت',
    'L/h': 'لیتر/ساعت',
    'L/ha': 'لیتر/هکتار',
    'mL/L': 'میلی‌لیتر/لیتر',
    'kg': 'کیلوگرم',
    'kg/ha': 'کیلوگرم/هکتار',
    'ton': 'تن',
    '%': 'درصد',
    'min': 'دقیقه',
    'count': 'عدد',
    'bag': 'کیسه',
    'tank': 'مخزن',
    'Toman': 'تومان',
    'TOMAN': 'تومان',
    'selected_unit': 'واحد انتخابی',
    'ratio': 'ضریب',
  };
  return units[unit] ?? unit;
}

String formatToolboxValue(BuildContext context, double value, String unit) {
  if (unit == 'TOMAN') return formatToman(context, value);
  if (unit.startsWith('TOMAN/')) {
    final denominator = localizeToolboxUnit(context, unit.substring(6));
    return '${formatToman(context, value)}/$denominator';
  }
  final raw =
      value == value.roundToDouble()
          ? value.toStringAsFixed(0)
          : value.toStringAsFixed(2);
  final number = context.l10n.isFa ? toPersianDigits(raw) : raw;
  final localizedUnit = localizeToolboxUnit(context, unit);
  return localizedUnit.isEmpty ? number : '$number $localizedUnit';
}

String localizeToolboxError(BuildContext context, Object error) {
  if (error is ToolboxApiException) {
    if (error.isNotFound) {
      return context.l10n.tr(
        fa:
            'مسیر همگام‌سازی در نسخهٔ درحال‌اجرای سرور فعال نیست. پس از بارگذاری نسخهٔ جدید سرور، دوباره تلاش کنید.',
        en:
            'Sync is not enabled in the currently running server version. Retry after the new server version is loaded.',
      );
    }
    if (error.isOffline) {
      return context.l10n.tr(
        fa:
            'اینترنت یا سرور در دسترس نیست؛ محاسبه‌گرها همچنان بدون اینترنت کار می‌کنند.',
        en:
            'The internet or server is unavailable; calculators still work offline.',
      );
    }
    if (error.statusCode == 401) {
      return context.l10n.tr(
        fa: 'نشست شما پایان یافته است؛ دوباره وارد شوید.',
        en: 'Your session has expired; please sign in again.',
      );
    }
    if (error.statusCode == 403) {
      return context.l10n.tr(
        fa: 'برای همگام‌سازی این مزرعه دسترسی ندارید.',
        en: 'You do not have permission to sync this farm.',
      );
    }
  }
  return context.l10n.tr(
    fa: 'همگام‌سازی انجام نشد؛ دوباره تلاش کنید.',
    en: 'Sync failed; please try again.',
  );
}
