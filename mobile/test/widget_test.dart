import 'package:farm_net/app.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Farm Net app boots without framework errors', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: FarmNetApp(),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(tester.takeException(), isNull);
  });
}
