import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('login screen does not ship with demo credentials', () {
    final source =
        File(
          'lib/features/auth/presentation/login_screen.dart',
        ).readAsStringSync();

    expect(
      source,
      isNot(contains("TextEditingController(text: 'admin@example.com')")),
    );
    expect(source, isNot(contains("TextEditingController(text: 'change-me')")));
    expect(source, contains("context.push('/forgot-password')"));
    expect(source, contains('AuthPageShell'));
    expect(source, contains('mobileAlignment: const Alignment(0, -0.78)'));
    expect(
      source,
      contains('desktopAlignment: const AlignmentDirectional(1, -0.42)'),
    );
  });
}
