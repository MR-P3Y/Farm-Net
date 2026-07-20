import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/search_api.dart';
import '../data/search_models.dart';
import '../data/search_repository.dart';

class SearchState {
  const SearchState({
    this.isLoading = false,
    this.hasSearched = false,
    this.query = '',
    this.types = searchResultTypes,
    this.sort = 'relevance',
    this.result,
    this.errorMessage,
  });
  final bool isLoading;
  final bool hasSearched;
  final String query;
  final List<String> types;
  final String sort;
  final UnifiedSearchResult? result;
  final String? errorMessage;

  SearchState copyWith({
    bool? isLoading,
    bool? hasSearched,
    String? query,
    List<String>? types,
    String? sort,
    UnifiedSearchResult? result,
    String? errorMessage,
    bool clearError = false,
  }) => SearchState(
    isLoading: isLoading ?? this.isLoading,
    hasSearched: hasSearched ?? this.hasSearched,
    query: query ?? this.query,
    types: types ?? this.types,
    sort: sort ?? this.sort,
    result: result ?? this.result,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
  );
}

final searchControllerProvider =
    StateNotifierProvider<SearchController, SearchState>(
      (ref) => SearchController(ref.watch(searchRepositoryProvider)),
    );

class SearchController extends StateNotifier<SearchState> {
  SearchController(this._repository) : super(const SearchState());
  final SearchRepository _repository;

  void toggleType(String type) {
    final next = [...state.types];
    next.contains(type) ? next.remove(type) : next.add(type);
    if (next.isNotEmpty) state = state.copyWith(types: next);
  }

  void setSort(String sort) => state = state.copyWith(sort: sort);

  Future<void> search(String rawQuery) async {
    final query = rawQuery.trim();
    if (query.length < 2) {
      state = state.copyWith(
        errorMessage: 'عبارت جستجو باید حداقل دو نویسه باشد.',
      );
      return;
    }
    state = state.copyWith(isLoading: true, query: query, clearError: true);
    try {
      final result = await _repository.search(
        query: query,
        types: state.types,
        sort: state.sort,
      );
      state = state.copyWith(
        isLoading: false,
        hasSearched: true,
        result: result,
      );
    } on SearchApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        hasSearched: true,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        hasSearched: true,
        errorMessage: 'جستجو انجام نشد. دوباره تلاش کنید.',
      );
    }
  }
}
