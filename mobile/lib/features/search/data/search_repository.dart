import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'search_api.dart';
import 'search_models.dart';

final searchRepositoryProvider = Provider<SearchRepository>(
  (ref) => SearchRepository(api: SearchApi()),
);

class SearchRepository {
  const SearchRepository({required SearchApi api}) : _api = api;
  final SearchApi _api;

  Future<UnifiedSearchResult> search({
    required String query,
    required List<String> types,
    String sort = 'relevance',
  }) => _api.search(query: query, types: types, sort: sort);
}
