import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/network/api_error_mapper.dart';
import 'favorite_models.dart';

class FavoriteApiException implements Exception {
  const FavoriteApiException(this.error);

  final ApiError error;

  @override
  String toString() => error.message;
}

class FavoriteApi {
  FavoriteApi({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<List<FavoriteItem>> list({FavoriteSubjectType? subjectType}) async {
    try {
      final response = await _client.get(
        'favorites',
        queryParameters: {
          if (subjectType != null) 'subject_type': subjectType.apiValue,
          'page_size': 100,
        },
      );
      final rows = response.data?['data'] as List? ?? const [];
      return rows
          .map(
            (item) =>
                FavoriteItem.fromJson(Map<String, dynamic>.from(item as Map)),
          )
          .toList(growable: false);
    } on DioException catch (error) {
      throw FavoriteApiException(mapApiError(error));
    }
  }

  Future<Set<int>> status(
    FavoriteSubjectType subjectType,
    Iterable<int> subjectIds,
  ) async {
    final ids = subjectIds.toSet().toList(growable: false);
    if (ids.isEmpty) return const {};

    try {
      final response = await _client.get(
        'favorites/status/${subjectType.apiValue}',
        queryParameters: {'subject_ids': ids},
      );
      final rows =
          response.data?['data']?['favorite_subject_ids'] as List? ?? const [];
      return rows.map((item) => (item as num).toInt()).toSet();
    } on DioException catch (error) {
      throw FavoriteApiException(mapApiError(error));
    }
  }

  Future<FavoriteItem> add(
    FavoriteSubjectType subjectType,
    int subjectId,
  ) async {
    try {
      final response = await _client.put(
        'favorites/${subjectType.apiValue}/$subjectId',
      );
      return FavoriteItem.fromJson(
        Map<String, dynamic>.from(response.data?['data'] as Map),
      );
    } on DioException catch (error) {
      throw FavoriteApiException(mapApiError(error));
    }
  }

  Future<void> remove(FavoriteSubjectType subjectType, int subjectId) async {
    try {
      await _client.delete('favorites/${subjectType.apiValue}/$subjectId');
    } on DioException catch (error) {
      throw FavoriteApiException(mapApiError(error));
    }
  }
}
