import 'package:farm_net/features/consultants/data/consultant_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('public consultant parses backend decimal rating strings', () {
    final consultant = ConsultantProfileModel.fromJson({
      'id': 1,
      'user_id': 23,
      'display_name': 'دکتر سارا کشاورز',
      'status': 'approved',
      'is_verified': true,
      'is_featured': false,
      'rating_average': '4.75',
      'reviews_count': 12,
      'requests_count': 20,
      'completed_requests_count': 17,
      'specialties': <Map<String, dynamic>>[],
    });

    expect(consultant.ratingAverage, 4.75);
    expect(consultant.resolvedName, 'دکتر سارا کشاورز');
  });

  test('missing or invalid rating safely falls back to zero', () {
    final consultant = ConsultantProfileModel.fromJson({
      'id': 2,
      'user_id': 24,
      'status': 'approved',
      'rating_average': null,
    });

    expect(consultant.ratingAverage, 0);
  });
}
