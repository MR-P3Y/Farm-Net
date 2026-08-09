import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/favorites/data/favorite_api.dart';
import 'package:farm_net/features/favorites/data/favorite_models.dart';
import 'package:farm_net/features/favorites/data/favorite_repository.dart';
import 'package:farm_net/features/favorites/presentation/favorite_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'shared favorite button loads status and toggles optimistically',
    (tester) async {
      final repository = _FakeFavoriteRepository();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [favoriteRepositoryProvider.overrideWithValue(repository)],
          child: MaterialApp(
            locale: const Locale('fa'),
            supportedLocales: AppLocalizations.supportedLocales,
            localizationsDelegates: const [
              AppLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            theme: AppTheme.light(const Locale('fa')),
            home: const Scaffold(
              body: FavoriteIconButton(
                subjectType: FavoriteSubjectType.serviceOffer,
                subjectId: 14,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.favorite_border_rounded), findsOne);
      await tester.tap(find.byIcon(Icons.favorite_border_rounded));
      await tester.pumpAndSettle();

      expect(repository.added, 14);
      expect(find.byIcon(Icons.favorite_rounded), findsOne);
      expect(find.text('به علاقه‌مندی‌ها اضافه شد.'), findsOne);
    },
  );
}

class _FakeFavoriteRepository extends FavoriteRepository {
  _FakeFavoriteRepository() : super(api: FavoriteApi());

  int? added;

  @override
  Future<Set<int>> status(
    FavoriteSubjectType subjectType,
    Iterable<int> subjectIds,
  ) async => const {};

  @override
  Future<FavoriteItem> add(
    FavoriteSubjectType subjectType,
    int subjectId,
  ) async {
    added = subjectId;
    return FavoriteItem(
      id: 1,
      subjectType: subjectType,
      subjectId: subjectId,
      isAvailable: true,
      createdAt: DateTime(2026, 8, 10),
    );
  }

  @override
  Future<void> remove(FavoriteSubjectType subjectType, int subjectId) async {}
}
