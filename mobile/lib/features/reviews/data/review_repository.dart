import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'review_api.dart';
import 'review_models.dart';

final reviewRepositoryProvider = Provider<ReviewRepository>(
  (ref) => ReviewRepository(),
);

class ReviewRepository {
  ReviewRepository({ReviewApi? api}) : _api = api ?? ReviewApi();
  final ReviewApi _api;

  Future<PublicReviewPage> publicReviews(String type, int id) =>
      _api.publicReviews(type, id);
  Future<List<MyReview>> myReviews() => _api.myReviews();
  Future<MyReview> create(ReviewCreateTarget target, int score, String? body) =>
      _api.create(target, score, body);
  Future<MyReview> update(int id, int score, String? body) =>
      _api.update(id, score, body);
  Future<void> delete(int id) => _api.delete(id);
}
