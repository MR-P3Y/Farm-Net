String normalizeToolboxNumber(String value) {
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

double? parseToolboxNumber(String value) {
  final normalized = normalizeToolboxNumber(value);
  return normalized.isEmpty ? null : double.tryParse(normalized);
}

String formatToolboxNumberInput(double? value) {
  if (value == null) return '';
  return value == value.roundToDouble()
      ? value.toStringAsFixed(0)
      : value.toString();
}
