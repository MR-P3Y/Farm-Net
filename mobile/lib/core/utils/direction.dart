import 'package:flutter/material.dart';

bool isPersianLocale(BuildContext context) {
  return Localizations.localeOf(context).languageCode == 'fa';
}

TextDirection appTextDirection(BuildContext context) {
  return isPersianLocale(context) ? TextDirection.rtl : TextDirection.ltr;
}
