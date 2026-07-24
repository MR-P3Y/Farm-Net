import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error_mapper.dart';
import 'review_models.dart';

class ReviewApiException implements Exception {
  const ReviewApiException(this.message);
  final String message;
  @override
  String toString() => message;
}

class ReviewApi {
  ReviewApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final ApiClient _client;

  Future<PublicReviewPage> publicReviews(
    String subjectType,
    int subjectId,
  ) async {
    final json = await _get('/reviews/subjects/$subjectType/$subjectId');
    final meta = (json['meta'] as Map?)?.cast<String, dynamic>() ?? {};
    return PublicReviewPage(
      items: (json['data'] as List? ?? const [])
          .map((e) => PublicReview.fromJson((e as Map).cast<String, dynamic>()))
          .toList(),
      rating: RatingSummary.fromJson(
        (meta['rating'] as Map?)?.cast<String, dynamic>() ?? {},
      ),
    );
  }

  Future<List<MyReview>> myReviews() async {
    final json = await _get('/reviews/me');
    return (json['data'] as List? ?? const [])
        .map((e) => MyReview.fromJson((e as Map).cast<String, dynamic>()))
        .toList();
  }

  Future<MyReview> create(ReviewCreateTarget target, int score, String? body) {
    return _mutation('/reviews', {
      'source_type': target.sourceType,
      'source_id': target.sourceId,
      'subject_type': target.subjectType,
      'subject_id': target.subjectId,
      'score': score,
      'body': body,
    }, post: true);
  }

  Future<MyReview> update(int id, int score, String? body) =>
      _mutation('/reviews/me/$id', {'score': score, 'body': body});

  Future<void> delete(int id) async {
    try {
      await _client.delete('/reviews/me/$id');
    } on DioException catch (error) {
      throw ReviewApiException(mapApiError(error).message);
    }
  }

  Future<MyReview> _mutation(
    String path,
    Map<String, dynamic> data, {
    bool post = false,
  }) async {
    try {
      final response = post
          ? await _client.post(path, data: data)
          : await _client.patch(path, data: data);
      final json = (response.data as Map).cast<String, dynamic>();
      return MyReview.fromJson((json['data'] as Map).cast<String, dynamic>());
    } on DioException catch (error) {
      throw ReviewApiException(mapApiError(error).message);
    }
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.get(path);
      return (response.data as Map).cast<String, dynamic>();
    } on DioException catch (error) {
      throw ReviewApiException(mapApiError(error).message);
    }
  }
}
