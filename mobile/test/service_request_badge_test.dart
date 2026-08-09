import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/core/widgets/farm_app_bar.dart';
import 'package:farm_net/features/services/presentation/service_request_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('service request count stays inside its app bar action', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(320, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_badgeApp(7));
    await tester.pumpAndSettle();

    final actionRect = tester.getRect(
      find.byKey(const Key('service-my-requests-action')),
    );
    final badgeRect = tester.getRect(find.text('۷'));

    expect(
      actionRect.contains(badgeRect.topLeft),
      isTrue,
      reason: 'action=$actionRect badge=$badgeRect',
    );
    expect(
      actionRect.contains(badgeRect.bottomRight),
      isTrue,
      reason: 'action=$actionRect badge=$badgeRect',
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('large service request counts stay compact inside the action', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(320, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_badgeApp(107));
    await tester.pumpAndSettle();

    final actionRect = tester.getRect(
      find.byKey(const Key('service-my-requests-action')),
    );
    final badgeRect = tester.getRect(find.text('۹۹+'));

    expect(
      actionRect.contains(badgeRect.topLeft),
      isTrue,
      reason: 'action=$actionRect badge=$badgeRect',
    );
    expect(
      actionRect.contains(badgeRect.bottomRight),
      isTrue,
      reason: 'action=$actionRect badge=$badgeRect',
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('English request badge also stays inside the app bar action', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(320, 640));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_badgeApp(107, locale: const Locale('en')));
    await tester.pumpAndSettle();

    final actionRect = tester.getRect(
      find.byKey(const Key('service-my-requests-action')),
    );
    final badgeRect = tester.getRect(find.text('99+'));

    expect(actionRect.contains(badgeRect.topLeft), isTrue);
    expect(actionRect.contains(badgeRect.bottomRight), isTrue);
    expect(tester.takeException(), isNull);
  });
}

Widget _badgeApp(int count, {Locale locale = const Locale('fa')}) {
  return ProviderScope(
    overrides: [
      activeServiceRequestCountProvider.overrideWith((ref) async => count),
    ],
    child: MaterialApp(
      locale: locale,
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: AppTheme.light(locale),
      home: const Scaffold(
        appBar: FarmAppBar(
          title: 'خدمات کشاورزی',
          showBack: false,
          actions: [MyServiceRequestsAction()],
        ),
      ),
    ),
  );
}
