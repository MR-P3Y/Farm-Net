import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/features/farms/data/farm_models.dart';
import 'package:farm_net/features/farms/presentation/widgets/farm_location_search_sheet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'location result parses coordinates and stable internal geo payload',
    () {
      final result = FarmLocationResult.fromJson({
        'reference': 'place-1',
        'display_name': 'قلات، شیراز، فارس',
        'short_name': 'قلات',
        'latitude': '29.8051',
        'longitude': '52.4897',
        'provider': 'openstreetmap',
        'attribution': '© OpenStreetMap contributors',
        'province_id': 1,
        'county_id': 2,
        'district_id': 3,
        'rural_district_id': 4,
        'village_id': 6,
      });

      expect(result.latitude, 29.8051);
      expect(result.longitude, 52.4897);
      expect(result.hasInternalGeoMatch, isTrue);
      expect(result.geoPayload, {
        'province_id': 1,
        'county_id': 2,
        'district_id': 3,
        'rural_district_id': 4,
        'village_id': 6,
      });
    },
  );

  testWidgets('search sheet calls Backend only after explicit submit', (
    tester,
  ) async {
    var calls = 0;
    FarmLocationResult? selected;
    await tester.pumpWidget(
      _Harness(
        locale: const Locale('fa'),
        onOpen: (context) async {
          selected = await showFarmLocationSearchSheet(
            context,
            onSearch: (query) async {
              calls++;
              expect(query, 'قلات شیراز');
              return const [
                FarmLocationResult(
                  reference: 'place-1',
                  displayName: 'قلات، شهرستان شیراز، استان فارس، ایران',
                  shortName: 'قلات',
                  latitude: 29.8051,
                  longitude: 52.4897,
                  provider: 'openstreetmap',
                  attribution: '© OpenStreetMap contributors',
                ),
              ];
            },
          );
        },
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const ValueKey('farm-location-search-field')),
      'قلات شیراز',
    );
    await tester.pump();
    expect(calls, 0);

    await tester.tap(find.byKey(const ValueKey('farm-location-search-submit')));
    await tester.pumpAndSettle();
    expect(calls, 1);
    expect(find.text('قلات'), findsOneWidget);
    expect(find.text('© OpenStreetMap contributors'), findsOneWidget);

    await tester.tap(find.text('قلات'));
    await tester.pumpAndSettle();
    expect(selected?.reference, 'place-1');
  });

  testWidgets('English search sheet remains fully English', (tester) async {
    await tester.pumpWidget(
      _Harness(
        locale: const Locale('en'),
        onOpen: (context) async {
          await showFarmLocationSearchSheet(
            context,
            onSearch: (_) async => const [],
          );
        },
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.text('Find farm location'), findsOneWidget);
    expect(find.text('Search'), findsOneWidget);
    expect(find.textContaining('نام استان'), findsNothing);
  });
}

class _Harness extends StatelessWidget {
  const _Harness({required this.locale, required this.onOpen});

  final Locale locale;
  final Future<void> Function(BuildContext context) onOpen;

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
    home: Builder(
      builder:
          (context) => Scaffold(
            body: FilledButton(
              onPressed: () => onOpen(context),
              child: const Text('Open'),
            ),
          ),
    ),
  );
}
