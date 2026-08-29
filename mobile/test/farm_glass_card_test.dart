import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/core/widgets/farm_glass_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('glass cards use backdrop blur by default', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(const Locale('en')),
        home: const Scaffold(body: FarmGlassCard(child: Text('content'))),
      ),
    );

    expect(find.byType(BackdropFilter), findsOneWidget);
    expect(find.text('content'), findsOneWidget);
  });

  testWidgets('backdrop blur can still be disabled explicitly', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(const Locale('en')),
        home: const Scaffold(
          body: FarmGlassCard(enableBlur: false, child: Text('content')),
        ),
      ),
    );

    expect(find.byType(BackdropFilter), findsNothing);
  });
}
