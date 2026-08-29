import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'mobile account security API follows the protected backend contract',
    () {
      final source =
          File('lib/features/auth/data/auth_api.dart').readAsStringSync();

      expect(source, contains("_get('auth/sessions')"));
      expect(source, contains("_delete('auth/sessions/\$sessionId')"));
      expect(source, contains("'auth/sessions/revoke-others'"));
      expect(source, contains("'auth/password/change'"));
    },
  );
}
