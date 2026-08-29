import 'package:farm_net/features/profile/data/profile_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('profile update serializes only fields managed by the editor', () {
    const input = ProfileUpdateInput(
      firstName: 'علی',
      lastName: 'کشاورز',
      displayName: '',
      nationalId: '1234567890',
      birthDate: null,
      gender: '',
      provinceId: 1,
      countyId: 2,
      cityId: null,
      address: 'نشانی',
      postalCode: '',
      avatarFileId: 'owned-avatar-key',
      bio: '',
    );

    final json = input.toJson();

    expect(json['birth_date'], isNull);
    expect(json['gender'], '');
    expect(json['city_id'], isNull);
    expect(json, isNot(contains('district_id')));
    expect(json, isNot(contains('rural_district_id')));
    expect(json, isNot(contains('village_id')));
    expect(json['avatar_file_id'], 'owned-avatar-key');
  });

  test(
    'profile model retains hidden backend fields for safe display state',
    () {
      final profile = UserProfile.fromJson({
        'id': 1,
        'user_id': 7,
        'district_id': 3,
        'rural_district_id': 4,
        'village_id': 6,
        'avatar_file_id': 'avatar-key',
        'avatar_url': '/api/v1/media/public/avatar-key',
        'profile_completed': true,
      });

      expect(profile.districtId, 3);
      expect(profile.ruralDistrictId, 4);
      expect(profile.villageId, 6);
      expect(profile.avatarFileId, 'avatar-key');
      expect(profile.avatarUrl, '/api/v1/media/public/avatar-key');
    },
  );
}
