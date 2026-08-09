import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'favorite_api.dart';
import 'favorite_models.dart';

final favoriteRepositoryProvider = Provider<FavoriteRepository>(
  (ref) => FavoriteRepository(api: FavoriteApi()),
);

class FavoriteRepository {
  const FavoriteRepository({required FavoriteApi api}) : _api = api;

  final FavoriteApi _api;

  Future<List<FavoriteItem>> list({FavoriteSubjectType? subjectType}) =>
      _api.list(subjectType: subjectType);

  Future<Set<int>> status(
    FavoriteSubjectType subjectType,
    Iterable<int> subjectIds,
  ) => _api.status(subjectType, subjectIds);

  Future<FavoriteItem> add(FavoriteSubjectType subjectType, int subjectId) =>
      _api.add(subjectType, subjectId);

  Future<void> remove(FavoriteSubjectType subjectType, int subjectId) =>
      _api.remove(subjectType, subjectId);
}
