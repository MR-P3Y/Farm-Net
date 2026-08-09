import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/services/data/service_models.dart';
import 'package:farm_net/features/services/presentation/service_list_screen.dart';
import 'package:farm_net/features/services/presentation/service_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const spraying = ServiceCategory(id: 1, code: 'spraying', title: 'سم‌پاشی');
  const irrigation = ServiceCategory(
    id: 7,
    code: 'irrigation_installation',
    title: 'نصب آبیاری',
  );

  test('service categories use stable backend codes for their icons', () {
    expect(serviceCategoryIcon(spraying), Icons.water_drop_outlined);
    expect(serviceCategoryIcon(irrigation), Icons.water_outlined);
  });

  testWidgets('quick categories expose all items and select immediately', (
    tester,
  ) async {
    int? selected = -1;
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: ServiceCategoryQuickFilter(
          categories: const [spraying, irrigation],
          selectedCategoryId: null,
          onSelected: (value) => selected = value,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('service-category-quick-filter')), findsOne);
    expect(find.text('همه'), findsOne);
    expect(find.text('سم‌پاشی'), findsOne);

    await tester.tap(find.text('سم‌پاشی'));
    await tester.pump();
    expect(selected, 1);
  });

  testWidgets('service price follows Persian locale and Toman formatting', (
    tester,
  ) async {
    const offer = ServiceOffer(
      id: 3,
      providerProfileId: 4,
      title: 'سم‌پاشی پهپادی',
      pricingType: 'hectare',
      priceAmount: 1280000,
      currency: 'TOMAN',
      media: [],
    );

    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: Builder(
          builder: (context) => Text(servicePriceLabel(context, offer)),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('تومان'), findsOne);
    expect(find.textContaining('هکتاری'), findsOne);
    expect(find.textContaining('۱'), findsOne);
  });

  testWidgets('service price follows English locale', (tester) async {
    const offer = ServiceOffer(
      id: 3,
      providerProfileId: 4,
      title: 'Drone spraying',
      pricingType: 'hectare',
      priceAmount: 1280000,
      currency: 'TOMAN',
      media: [],
    );

    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('en'),
        child: Builder(
          builder: (context) => Text(servicePriceLabel(context, offer)),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('Toman'), findsOne);
    expect(find.textContaining('Per hectare'), findsOne);
  });
}

Widget _localizedApp({required Locale locale, required Widget child}) {
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
    home: Scaffold(body: child),
  );
}
