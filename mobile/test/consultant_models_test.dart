import 'package:farm_net/features/consultants/data/consultant_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ConsultantProfileModel', () {
    test('parses public consultant list item safely', () {
      final consultant = ConsultantProfileModel.fromJson({
        'consultant_id': 12,
        'user_id': 4,
        'display_name': 'مشاور خاک',
        'title': 'متخصص تغذیه گیاه',
        'province_name': 'گلستان',
        'city_name': 'گرگان',
        'status': 'approved',
        'is_verified': true,
        'is_featured': false,
        'rating_average': 4.5,
        'reviews_count': 8,
        'requests_count': 19,
        'completed_requests_count': 15,
        'specialties': [
          {'id': 2, 'code': 'soil', 'title': 'خاک'},
        ],
      });

      expect(consultant.id, 12);
      expect(consultant.resolvedName, 'مشاور خاک');
      expect(consultant.locationText, 'گلستان، گرگان');
      expect(consultant.specialties.single.title, 'خاک');
    });

    test('falls back when optional public fields are missing', () {
      final consultant = ConsultantProfileModel.fromJson({
        'id': 9,
        'user_id': 5,
      });

      expect(consultant.id, 9);
      expect(consultant.resolvedName, 'مشاور');
      expect(consultant.locationText, 'موقعیت ثبت نشده');
      expect(consultant.specialties, isEmpty);
    });
  });
}
