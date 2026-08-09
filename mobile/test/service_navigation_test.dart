import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/core/widgets/farm_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

void main() {
  testWidgets('direct service page shows back and uses its safe fallback', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/detail',
      routes: [
        GoRoute(
          path: '/list',
          builder: (_, _) => const Scaffold(body: Text('SERVICE-LIST')),
        ),
        GoRoute(
          path: '/detail',
          builder:
              (_, _) => const Scaffold(
                appBar: FarmAppBar(
                  title: 'SERVICE-DETAIL',
                  fallbackLocation: '/list',
                ),
              ),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(_TestApp(router: router));
    await tester.pumpAndSettle();

    expect(find.byTooltip('Back'), findsOneWidget);
    await tester.tap(find.byTooltip('Back'));
    await tester.pumpAndSettle();

    expect(router.routeInformationProvider.value.uri.path, '/list');
    expect(find.text('SERVICE-LIST'), findsOneWidget);
  });

  testWidgets('service back prefers the real previous page over fallback', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/origin',
      routes: [
        GoRoute(
          path: '/origin',
          builder: (_, _) => const Scaffold(body: Text('REAL-ORIGIN')),
        ),
        GoRoute(
          path: '/fallback',
          builder: (_, _) => const Scaffold(body: Text('FALLBACK')),
        ),
        GoRoute(
          path: '/detail',
          builder:
              (_, _) => const Scaffold(
                appBar: FarmAppBar(
                  title: 'SERVICE-DETAIL',
                  fallbackLocation: '/fallback',
                ),
              ),
        ),
      ],
    );
    addTearDown(router.dispose);

    await tester.pumpWidget(_TestApp(router: router));
    await tester.pumpAndSettle();
    final popped = router.push<void>('/detail');
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Back'));
    await tester.pumpAndSettle();
    await popped;

    expect(router.routeInformationProvider.value.uri.path, '/origin');
    expect(find.text('REAL-ORIGIN'), findsOneWidget);
    expect(find.text('FALLBACK'), findsNothing);
  });
}

class _TestApp extends StatelessWidget {
  const _TestApp({required this.router});

  final GoRouter router;

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: router,
      locale: const Locale('en'),
      theme: AppTheme.light(const Locale('en')),
      darkTheme: AppTheme.dark(const Locale('en')),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}
