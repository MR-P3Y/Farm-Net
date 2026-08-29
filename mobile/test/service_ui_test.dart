import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/services/data/service_models.dart';
import 'package:farm_net/features/services/presentation/service_final_price_card.dart';
import 'package:farm_net/features/services/presentation/service_floating_action_bar.dart';
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

  testWidgets('fixed backend timeline notes follow the active locale', (
    tester,
  ) async {
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: Builder(
          builder:
              (context) => Text(
                serviceStatusNoteLabel(context, 'Service request created'),
              ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('درخواست خدمت ثبت شد'), findsOne);
    expect(find.text('Service request created'), findsNothing);
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

  testWidgets('requester can pay an accepted final price in Persian', (
    tester,
  ) async {
    var payPressed = false;
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: ServiceFinalPriceCard(
          finalPrice: const ServiceFinalPrice(
            id: 1,
            sourceId: 21,
            version: 1,
            amount: 1500000,
            currency: 'TOMAN',
            description: 'سم‌پاشی کامل قطعه',
            status: 'accepted',
            proposedAt: '2026-08-10T12:30:00Z',
            invoiceId: 17,
            invoiceStatus: 'payment_pending',
          ),
          providerView: false,
          isSaving: false,
          onPay: () => payPressed = true,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('قیمت نهایی و پرداخت'), findsOne);
    expect(find.textContaining('تومان'), findsOne);
    expect(find.textContaining('۱۴۰۵'), findsOne);
    expect(find.text('پرداخت امن فاکتور'), findsOne);

    await tester.tap(find.text('پرداخت امن فاکتور'));
    expect(payPressed, isTrue);
  });

  testWidgets('missing final price never renders a zero amount', (
    tester,
  ) async {
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: const ServiceFinalPriceCard(
          finalPrice: null,
          providerView: true,
          isSaving: false,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('۰ تومان'), findsNothing);
    expect(find.textContaining('مبلغ قطعی'), findsOne);
  });

  testWidgets('service actions stay together in the floating bottom panel', (
    tester,
  ) async {
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: const ServiceFloatingActionBar(
          primary: ServiceAction(
            label: 'پذیرش و تعیین قیمت',
            icon: Icons.price_check,
            onPressed: null,
          ),
          secondary: ServiceAction(
            label: 'رد درخواست',
            icon: Icons.close,
            onPressed: null,
          ),
          tertiary: ServiceAction(
            label: 'لغو درخواست',
            icon: Icons.cancel_outlined,
            onPressed: null,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('پذیرش و تعیین قیمت'), findsOne);
    expect(find.text('رد درخواست'), findsOne);
    expect(find.text('لغو درخواست'), findsOne);
  });

  testWidgets('provider sees verified payment in English dark theme', (
    tester,
  ) async {
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('en'),
        dark: true,
        child: const ServiceFinalPriceCard(
          finalPrice: ServiceFinalPrice(
            id: 2,
            sourceId: 22,
            version: 1,
            amount: 2750000,
            currency: 'TOMAN',
            description: 'Completed service scope',
            status: 'accepted',
            proposedAt: '2026-08-10T12:30:00Z',
            invoiceId: 18,
            invoiceStatus: 'paid',
          ),
          providerView: true,
          isSaving: false,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Final price and payment'), findsOne);
    expect(find.textContaining('Toman'), findsOne);
    expect(find.text('Payment has been verified.'), findsOne);
    expect(find.text('Pay invoice securely'), findsNothing);
  });

  testWidgets('refund state is explicit in Persian', (tester) async {
    await tester.pumpWidget(
      _localizedApp(
        locale: const Locale('fa'),
        child: const ServiceFinalPriceCard(
          finalPrice: ServiceFinalPrice(
            id: 3,
            sourceId: 23,
            version: 1,
            amount: 1800000,
            currency: 'TOMAN',
            description: 'خدمت کامل',
            status: 'accepted',
            proposedAt: '2026-08-10T12:30:00Z',
            invoiceId: 19,
            invoiceStatus: 'refund_pending',
            refundId: 4,
            refundStatus: 'requested',
            refundReviewRequired: true,
          ),
          providerView: false,
          isSaving: false,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('در انتظار بررسی ادمین'), findsOne);
    expect(find.textContaining('درخواست بازپرداخت'), findsOne);
    expect(find.text('پرداخت امن فاکتور'), findsNothing);
  });
}

Widget _localizedApp({
  required Locale locale,
  required Widget child,
  bool dark = false,
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
    themeMode: dark ? ThemeMode.dark : ThemeMode.light,
    home: Scaffold(body: child),
  );
}
