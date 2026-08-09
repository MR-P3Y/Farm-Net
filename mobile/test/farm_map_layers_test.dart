import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/features/farms/presentation/widgets/farm_map_layers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('map styles expose distinct street and satellite sources', () {
    expect(FarmMapStyle.street.tileUrlTemplate, contains('openstreetmap.org'));
    expect(FarmMapStyle.satellite.tileUrlTemplate, contains('World_Imagery'));
    expect(FarmMapStyle.satellite.tileUrlTemplate, contains('{z}/{y}/{x}'));
    expect(FarmMapStyle.street.attribution, contains('OpenStreetMap'));
    expect(FarmMapStyle.satellite.attribution, contains('Esri'));
  });

  testWidgets('Persian map layer toggle selects satellite imagery', (
    tester,
  ) async {
    var selected = FarmMapStyle.street;
    await tester.pumpWidget(
      _Harness(
        locale: const Locale('fa'),
        child: StatefulBuilder(
          builder:
              (context, setState) => FarmMapLayerToggle(
                value: selected,
                onChanged: (value) => setState(() => selected = value),
              ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final control = tester.widget<SegmentedButton<FarmMapStyle>>(
      find.byType(SegmentedButton<FarmMapStyle>),
    );
    expect(control.segments.map((segment) => (segment.label! as Text).data), [
      'خیابانی',
      'ماهواره‌ای',
    ]);
    await tester.tap(find.byKey(const ValueKey('farm-map-style-satellite')));
    await tester.pumpAndSettle();
    expect(selected, FarmMapStyle.satellite);
  });

  testWidgets('English map layer toggle stays fully English', (tester) async {
    await tester.pumpWidget(
      _Harness(
        locale: const Locale('en'),
        child: FarmMapLayerToggle(
          value: FarmMapStyle.satellite,
          onChanged: (_) {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final control = tester.widget<SegmentedButton<FarmMapStyle>>(
      find.byType(SegmentedButton<FarmMapStyle>),
    );
    expect(control.segments.map((segment) => (segment.label! as Text).data), [
      'Street',
      'Satellite',
    ]);
  });
}

class _Harness extends StatelessWidget {
  const _Harness({required this.locale, required this.child});

  final Locale locale;
  final Widget child;

  @override
  Widget build(BuildContext context) => MaterialApp(
    locale: locale,
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    home: Scaffold(body: Center(child: child)),
  );
}
