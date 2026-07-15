import 'package:farm_net/features/social/data/social_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SocialPostModel expert answers', () {
    test('defaults to empty expert answers when field is missing', () {
      final post = SocialPostModel.fromJson(_postJson());

      expect(post.expertAnswers, isEmpty);
    });

    test('parses expert answer and safe consultant summary', () {
      final post = SocialPostModel.fromJson(
        _postJson(
          expertAnswers: [
            {
              'answer_id': 50,
              'post_id': 10,
              'expert_id': 2,
              'expert_user_id': 2,
              'body': 'پاسخ تخصصی',
              'status': 'published',
              'is_accepted': true,
              'helpful_count': 3,
              'reports_count': 0,
              'created_at': '2026-06-22T10:00:00',
              'updated_at': '2026-06-22T10:00:00',
              'consultant': {
                'consultant_id': 20,
                'user_id': 2,
                'display_name': 'دکتر کشاورز',
                'title': 'مشاور خاک',
                'status': 'approved',
                'is_verified': true,
                'is_featured': true,
                'rating_average': 4.8,
                'reviews_count': 12,
                'specialties': [
                  {'id': 1, 'code': 'soil', 'title': 'خاک'},
                ],
              },
            },
          ],
        ),
      );

      expect(post.expertAnswers, hasLength(1));
      expect(post.expertAnswers.first.id, 50);
      expect(post.expertAnswers.first.consultant?.consultantId, 20);
      expect(post.expertAnswers.first.consultant?.resolvedName, 'دکتر کشاورز');
      expect(
        post.expertAnswers.first.consultant?.specialties.first.title,
        'خاک',
      );
    });

    test('keeps expert answer usable when consultant metadata is null', () {
      final post = SocialPostModel.fromJson(
        _postJson(
          expertAnswers: [
            {
              'answer_id': 51,
              'post_id': 10,
              'expert_user_id': 3,
              'body': 'پاسخ بدون پروفایل',
              'status': 'published',
              'is_accepted': false,
              'helpful_count': 0,
              'reports_count': 0,
              'created_at': '2026-06-22T10:00:00',
              'updated_at': '2026-06-22T10:00:00',
              'consultant': null,
            },
          ],
        ),
      );

      expect(post.expertAnswers.single.consultant, isNull);
      expect(post.expertAnswers.single.body, 'پاسخ بدون پروفایل');
    });
  });
}

Map<String, dynamic> _postJson({List<Map<String, dynamic>>? expertAnswers}) {
  return {
    'id': 10,
    'author_user_id': 1,
    'category_id': null,
    'title': 'عنوان پست',
    'body': 'متن پست',
    'post_type': 'question',
    'status': 'published',
    'visibility': 'public',
    'media_file_id': null,
    'media_public_url': null,
    'province_name': null,
    'city_name': null,
    'views_count': 1,
    'comments_count': 0,
    'reactions_count': 0,
    'reports_count': 0,
    'created_at': '2026-06-22T09:00:00',
    if (expertAnswers != null) 'expert_answers': expertAnswers,
  };
}
