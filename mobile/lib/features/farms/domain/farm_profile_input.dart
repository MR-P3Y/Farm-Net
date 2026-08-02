String normalizeFarmNumber(String value) {
  const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
  const arabicDigits = '٠١٢٣٤٥٦٧٨٩';
  var result = value.trim();
  for (var index = 0; index < 10; index++) {
    result = result
        .replaceAll(persianDigits[index], '$index')
        .replaceAll(arabicDigits[index], '$index');
  }
  return result
      .replaceAll('٬', '')
      .replaceAll('،', '')
      .replaceAll(',', '')
      .replaceAll('٫', '.');
}

double? parseFarmArea(String value) {
  final normalized = normalizeFarmNumber(value);
  if (normalized.isEmpty) return null;
  return double.tryParse(normalized);
}

String formatFarmAreaInput(double? value) {
  if (value == null) return '';
  if (value == value.roundToDouble()) return value.toStringAsFixed(0);
  return value.toString();
}
