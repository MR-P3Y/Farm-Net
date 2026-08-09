import 'package:farm_net/core/routing/app_router.dart';
import 'package:farm_net/features/settings/presentation/settings_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

void main() {
  test('the application router defines the settings route', () {
    expect(_containsPath(appRouter.configuration.routes, '/settings'), isTrue);
  });

  testWidgets('the settings screen renders its controls', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: SettingsScreen())),
    );

    expect(find.text('Settings'), findsOneWidget);
    expect(find.byType(SwitchListTile), findsOneWidget);
    expect(find.byIcon(Icons.language_rounded), findsOneWidget);
    expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
  });
}

bool _containsPath(List<RouteBase> routes, String path) {
  for (final route in routes) {
    if (route is GoRoute && route.path == path) return true;
    if (_containsPath(route.routes, path)) return true;
  }
  return false;
}
