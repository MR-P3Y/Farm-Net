import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('mobile profile API follows the live singular PATCH contract', () {
    final source =
        File('lib/features/profile/data/profile_api.dart').readAsStringSync();

    expect(source, contains("_client.get('profile/me')"));
    expect(source, contains("_client.patch('profile/me'"));
    expect(source, isNot(contains("'profiles/me'")));
    expect(source, isNot(contains("_client.put('profile/me'")));
  });
}
