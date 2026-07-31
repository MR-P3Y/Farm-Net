import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/core/widgets/farm_empty_view.dart';
import 'package:farm_net/core/widgets/farm_error_view.dart';
import 'package:farm_net/core/widgets/farm_glass_card.dart';
import 'package:farm_net/core/widgets/farm_loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app({
  required Widget child,
  Locale locale = const Locale('fa'),
  ThemeMode themeMode = ThemeMode.light,
}) {
  return MaterialApp(
    locale: locale,
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    theme: AppTheme.light(locale),
    darkTheme: AppTheme.dark(locale),
    themeMode: themeMode,
    home: Scaffold(body: child),
  );
}

void main() {
  testWidgets('common states use Persian localization', (tester) async {
    await tester.pumpWidget(_app(child: const FarmEmptyView()));
    await tester.pumpAndSettle();
    expect(find.text('موردی برای نمایش وجود ندارد'), findsOneWidget);

    await tester.pumpWidget(_app(child: const FarmLoadingView()));
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.text('در حال بارگذاری...'), findsOneWidget);
  });

  testWidgets('common error state uses English localization', (tester) async {
    await tester.pumpWidget(
      _app(child: const FarmErrorView(), locale: const Locale('en')),
    );
    await tester.pumpAndSettle();
    expect(find.text('Something went wrong'), findsOneWidget);
  });

  testWidgets('glass component renders in the dark theme', (tester) async {
    await tester.pumpWidget(
      _app(
        child: const FarmGlassCard(child: Text('content')),
        themeMode: ThemeMode.dark,
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('content'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
