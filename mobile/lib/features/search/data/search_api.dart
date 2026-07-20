import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'search_models.dart';

class SearchApiException implements Exception {
  const SearchApiException(this.error);
  final ApiError error;
}

class SearchApi {
  SearchApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final ApiClient _client;

  Future<UnifiedSearchResult> search({
    required String query,
    required List<String> types,
    String sort = 'relevance',
    int pageSize = 10,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/search',
        data: {
          'q': query.trim(),
          'types': types,
          'filters': {'currency': 'TOMAN'},
          'sort': sort,
          'page': 1,
          'page_size': pageSize,
        },
      );
      return UnifiedSearchResult.fromJson(
        response.data?['data'] as Map<String, dynamic>? ?? const {},
      );
    } on DioException catch (error) {
      final data = error.response?.data;
      throw SearchApiException(
        data is Map<String, dynamic>
            ? ApiError.fromJson(data)
            : ApiError(
              code: 'NETWORK_ERROR',
              message: error.message ?? 'Network error',
            ),
      );
    }
  }
}
