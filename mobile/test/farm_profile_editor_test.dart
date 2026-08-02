import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/farms/presentation/farm_profile_editor_screen.dart';
import 'package:farm_net/features/farms/presentation/widgets/farm_profile_action_dialogs.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('farm editor pre-fills the current profile', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: FarmProfileEditorScreen(
            farm: FarmModel(
              id: 7,
              name: 'North farm',
              status: 'active',
              description: 'Main greenhouse',
              declaredAreaSqm: 12500,
            ),
          ),
        ),
      ),
    );

    expect(find.text('Edit farm'), findsOneWidget);
    expect(find.text('North farm'), findsOneWidget);
    expect(find.text('Main greenhouse'), findsOneWidget);
    expect(find.text('12500'), findsOneWidget);
    expect(find.text('Save changes'), findsOneWidget);
  });

  testWidgets('farm editor requires a non-empty name before saving', (
    tester,
  ) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: FarmProfileEditorScreen())),
    );

    await tester.tap(find.text('Create farm'));
    await tester.pump();

    expect(find.text('Enter the farm name'), findsOneWidget);
  });

  testWidgets('remove confirmation explains that Farm history is preserved', (
    tester,
  ) async {
    const farm = FarmModel(id: 7, name: 'North farm', status: 'active');
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder:
              (context) => Scaffold(
                body: FilledButton(
                  onPressed: () => showFarmArchiveDialog(context, farm),
                  child: const Text('Open'),
                ),
              ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.text('Remove farm?'), findsOneWidget);
    expect(find.textContaining('history are preserved'), findsOneWidget);
    expect(find.text('Remove'), findsOneWidget);
  });
}
