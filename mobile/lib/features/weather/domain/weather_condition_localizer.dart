class WeatherConditionLocalizer {
  const WeatherConditionLocalizer._();

  static String label({
    required bool isFa,
    String? code,
    String? text,
    String fallback = '--',
  }) {
    final source = text?.trim();
    if (!isFa) {
      return source == null || source.isEmpty
          ? _englishByCode(code) ?? fallback
          : source;
    }
    final byCode = _persianByCode(code);
    if (byCode != null) return byCode;
    if (source == null || source.isEmpty) return fallback;
    return _persianByText[source.toLowerCase()] ?? source;
  }

  static String? _persianByCode(String? value) {
    final code = int.tryParse(value ?? '');
    if (code == null) return null;
    if (code >= 200 && code < 300) return 'رعدوبرق';
    if (code >= 300 && code < 400) return 'نم‌نم باران';
    if (code >= 500 && code < 600) {
      if (code == 500) return 'باران خفیف';
      if (code == 501) return 'باران متوسط';
      if (code >= 502) return 'باران شدید';
      return 'بارانی';
    }
    if (code >= 600 && code < 700) return 'برفی';
    if (code >= 700 && code < 800) {
      return switch (code) {
        701 => 'مه رقیق',
        711 => 'دودآلود',
        721 => 'غبارآلود',
        731 || 751 || 761 => 'گردوخاک',
        741 => 'مه‌آلود',
        762 => 'خاکستر آتشفشانی',
        771 => 'تندباد',
        781 => 'گردباد',
        _ => 'کاهش دید',
      };
    }
    return switch (code) {
      800 => 'آسمان صاف',
      801 => 'کمی ابری',
      802 => 'ابرهای پراکنده',
      803 => 'نیمه‌ابری',
      804 => 'ابری',
      _ => null,
    };
  }

  static String? _englishByCode(String? value) {
    final code = int.tryParse(value ?? '');
    return switch (code) {
      800 => 'clear sky',
      801 => 'few clouds',
      802 => 'scattered clouds',
      803 => 'broken clouds',
      804 => 'overcast clouds',
      _ => null,
    };
  }

  static const _persianByText = <String, String>{
    'clear': 'آسمان صاف',
    'clear sky': 'آسمان صاف',
    'few clouds': 'کمی ابری',
    'scattered clouds': 'ابرهای پراکنده',
    'broken clouds': 'نیمه‌ابری',
    'overcast clouds': 'ابری',
    'clouds': 'ابری',
    'light rain': 'باران خفیف',
    'moderate rain': 'باران متوسط',
    'heavy intensity rain': 'باران شدید',
    'very heavy rain': 'باران بسیار شدید',
    'shower rain': 'رگبار باران',
    'drizzle': 'نم‌نم باران',
    'thunderstorm': 'رعدوبرق',
    'snow': 'برف',
    'light snow': 'برف خفیف',
    'mist': 'مه رقیق',
    'fog': 'مه‌آلود',
    'haze': 'غبارآلود',
    'dust': 'گردوخاک',
    'sand': 'شن و گردوخاک',
    'smoke': 'دودآلود',
    'squall': 'تندباد',
    'tornado': 'گردباد',
  };
}
