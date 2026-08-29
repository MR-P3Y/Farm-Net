import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('mobile password reset follows the public backend contract', () {
    final source =
        File('lib/features/auth/data/auth_api.dart').readAsStringSync();

    expect(source, contains("'auth/password/reset/request'"));
    expect(source, contains("'auth/password/reset/confirm'"));
    expect(source, contains("'identifier': identifier"));
    expect(source, contains("'code': code"));
    expect(source, contains("'new_password': newPassword"));
  });
}
