import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('all feature date pickers use the shared locale-aware entry point', () {
    final violations = <String>[];
    for (final entity in Directory('lib').listSync(recursive: true)) {
      if (entity is! File || !entity.path.endsWith('.dart')) continue;
      final normalized = entity.path.replaceAll('\\', '/');
      if (normalized.endsWith('/core/utils/dates.dart')) continue;
      if (entity.readAsStringSync().contains('showDatePicker(')) {
        violations.add(normalized);
      }
    }

    expect(
      violations,
      isEmpty,
      reason:
          'Use showLocalizedDatePicker so Persian stays Jalali and English stays Gregorian.',
    );
  });
}
