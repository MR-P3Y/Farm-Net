import 'package:farm_net/core/utils/dates.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const delegate = JalaliCalendarDelegate();

  test('Jalali delegate round-trips Gregorian API dates', () {
    final gregorian = DateTime(2025, 3, 20);
    final jalali = delegate.toCalendarDate(gregorian);

    expect(jalali, DateTime(1403, 12, 30));
    expect(delegate.toGregorianDate(jalali), gregorian);
    expect(delegate.getDaysInMonth(1403, 12), 30);
    expect(
      delegate.addDaysToDate(DateTime(1403, 12, 30), 1),
      DateTime(1404, 1, 1),
    );
    expect(
      delegate.addMonthsToMonthDate(DateTime(1403, 12), 1),
      DateTime(1404, 1),
    );
  });

  test('Jalali delegate formats and parses Persian and Arabic digits', () {
    const localizations = DefaultMaterialLocalizations();
    final date = DateTime(1403, 12, 30);

    expect(delegate.formatMonthYear(date, localizations), 'اسفند ۱۴۰۳');
    expect(delegate.formatCompactDate(date, localizations), '۱۴۰۳/۱۲/۳۰');
    expect(delegate.parseCompactDate('١٤٠٣/١٢/٣٠', localizations), date);
    expect(delegate.parseCompactDate('۱۴۰۲/۱۲/۳۰', localizations), isNull);
  });

  testWidgets(
    'Persian picker renders Jalali month and returns Gregorian date',
    (tester) async {
      DateTime? selected;
      await tester.pumpWidget(
        _PickerHarness(
          locale: const Locale('fa'),
          onSelected: (value) => selected = value,
        ),
      );

      await tester.tap(find.text('open'));
      await tester.pumpAndSettle();

      expect(find.text('اسفند ۱۴۰۳'), findsOneWidget);
      expect(find.textContaining('2025'), findsNothing);

      await tester.tap(find.text('تأیید'));
      await tester.pumpAndSettle();
      expect(selected, DateTime(2025, 3, 20));
    },
  );

  testWidgets('English picker remains Gregorian', (tester) async {
    await tester.pumpWidget(const _PickerHarness(locale: Locale('en')));

    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();

    expect(find.text('March 2025'), findsOneWidget);
    expect(find.textContaining('۱۴۰۳'), findsNothing);
  });
}

class _PickerHarness extends StatelessWidget {
  const _PickerHarness({required this.locale, this.onSelected});

  final Locale locale;
  final ValueChanged<DateTime?>? onSelected;

  @override
  Widget build(BuildContext context) => MaterialApp(
    locale: locale,
    supportedLocales: const [Locale('fa'), Locale('en')],
    localizationsDelegates: const [
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    home: Scaffold(
      body: Builder(
        builder:
            (context) => TextButton(
              onPressed: () async {
                final value = await showLocalizedDatePicker(
                  context: context,
                  initialDate: DateTime(2025, 3, 20),
                  firstDate: DateTime(2024),
                  lastDate: DateTime(2026, 12, 31),
                );
                onSelected?.call(value);
              },
              child: const Text('open'),
            ),
      ),
    ),
  );
}
