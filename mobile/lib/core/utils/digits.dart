const Map<String, String> _enToFaDigits = {
  '0': '۰',
  '1': '۱',
  '2': '۲',
  '3': '۳',
  '4': '۴',
  '5': '۵',
  '6': '۶',
  '7': '۷',
  '8': '۸',
  '9': '۹',
};

const Map<String, String> _faToEnDigits = {
  '۰': '0',
  '۱': '1',
  '۲': '2',
  '۳': '3',
  '۴': '4',
  '۵': '5',
  '۶': '6',
  '۷': '7',
  '۸': '8',
  '۹': '9',
};

String toPersianDigits(Object? input) {
  var value = input?.toString() ?? '';
  _enToFaDigits.forEach((en, fa) {
    value = value.replaceAll(en, fa);
  });
  return value;
}

String toEnglishDigits(Object? input) {
  var value = input?.toString() ?? '';
  _faToEnDigits.forEach((fa, en) {
    value = value.replaceAll(fa, en);
  });
  return value;
}
