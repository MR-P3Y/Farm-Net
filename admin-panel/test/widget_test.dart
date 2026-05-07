import 'package:farm_net_admin/app.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Farm Net admin boots without framework errors', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: FarmNetAdminApp(),
      ),
    );
    await tester.pump();

    expect(tester.takeException(), isNull);
  });
}
