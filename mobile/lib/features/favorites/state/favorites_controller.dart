import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/favorite_api.dart';
import '../data/favorite_models.dart';
import '../data/favorite_repository.dart';

final favoritesControllerProvider =
    StateNotifierProvider<FavoritesController, FavoritesState>(
      (ref) => FavoritesController(
        repository: ref.watch(favoriteRepositoryProvider),
      ),
    );

class FavoritesState {
  const FavoritesState({
    this.items = const [],
    this.favoriteKeys = const {},
    this.loadingKeys = const {},
    this.isLoadingList = false,
    this.errorMessage,
  });

  final List<FavoriteItem> items;
  final Set<String> favoriteKeys;
  final Set<String> loadingKeys;
  final bool isLoadingList;
  final String? errorMessage;

  FavoritesState copyWith({
    List<FavoriteItem>? items,
    Set<String>? favoriteKeys,
    Set<String>? loadingKeys,
    bool? isLoadingList,
    String? errorMessage,
    bool clearError = false,
  }) {
    return FavoritesState(
      items: items ?? this.items,
      favoriteKeys: favoriteKeys ?? this.favoriteKeys,
      loadingKeys: loadingKeys ?? this.loadingKeys,
      isLoadingList: isLoadingList ?? this.isLoadingList,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}

class FavoritesController extends StateNotifier<FavoritesState> {
  FavoritesController({required FavoriteRepository repository})
    : _repository = repository,
      super(const FavoritesState());

  final FavoriteRepository _repository;

  static String key(FavoriteSubjectType type, int subjectId) =>
      '${type.apiValue}:$subjectId';

  bool isFavorite(FavoriteSubjectType type, int subjectId) =>
      state.favoriteKeys.contains(key(type, subjectId));

  bool isLoading(FavoriteSubjectType type, int subjectId) =>
      state.loadingKeys.contains(key(type, subjectId));

  Future<void> loadStatus(
    FavoriteSubjectType type,
    Iterable<int> subjectIds,
  ) async {
    final ids = subjectIds.toSet();
    if (ids.isEmpty) return;
    try {
      final favorites = await _repository.status(type, ids);
      final next = {...state.favoriteKeys};
      for (final id in ids) {
        next.remove(key(type, id));
      }
      for (final id in favorites) {
        next.add(key(type, id));
      }
      state = state.copyWith(favoriteKeys: next, clearError: true);
    } on FavoriteApiException catch (error) {
      state = state.copyWith(errorMessage: error.error.message);
    }
  }

  Future<bool> toggle(FavoriteSubjectType type, int subjectId) async {
    final itemKey = key(type, subjectId);
    if (state.loadingKeys.contains(itemKey)) {
      return state.favoriteKeys.contains(itemKey);
    }

    final wasFavorite = state.favoriteKeys.contains(itemKey);
    final nextFavorites = {...state.favoriteKeys};
    if (wasFavorite) {
      nextFavorites.remove(itemKey);
    } else {
      nextFavorites.add(itemKey);
    }
    state = state.copyWith(
      favoriteKeys: nextFavorites,
      loadingKeys: {...state.loadingKeys, itemKey},
      clearError: true,
    );

    try {
      if (wasFavorite) {
        await _repository.remove(type, subjectId);
      } else {
        await _repository.add(type, subjectId);
      }
      final nextItems =
          wasFavorite
              ? state.items
                  .where(
                    (item) =>
                        item.subjectType != type || item.subjectId != subjectId,
                  )
                  .toList(growable: false)
              : state.items;
      state = state.copyWith(
        items: nextItems,
        loadingKeys: {...state.loadingKeys}..remove(itemKey),
      );
      return !wasFavorite;
    } on FavoriteApiException catch (error) {
      final rolledBack = {...state.favoriteKeys};
      if (wasFavorite) {
        rolledBack.add(itemKey);
      } else {
        rolledBack.remove(itemKey);
      }
      state = state.copyWith(
        favoriteKeys: rolledBack,
        loadingKeys: {...state.loadingKeys}..remove(itemKey),
        errorMessage: error.error.message,
      );
      return wasFavorite;
    }
  }

  Future<void> loadList({FavoriteSubjectType? subjectType}) async {
    state = state.copyWith(isLoadingList: true, clearError: true);
    try {
      final items = await _repository.list(subjectType: subjectType);
      final favoriteKeys = {
        ...state.favoriteKeys,
        for (final item in items) key(item.subjectType, item.subjectId),
      };
      state = state.copyWith(
        items: items,
        favoriteKeys: favoriteKeys,
        isLoadingList: false,
      );
    } on FavoriteApiException catch (error) {
      state = state.copyWith(
        isLoadingList: false,
        errorMessage: error.error.message,
      );
    }
  }

  Future<void> removeItem(FavoriteItem item) async {
    if (!isFavorite(item.subjectType, item.subjectId)) return;
    await toggle(item.subjectType, item.subjectId);
  }
}
