class UserProfile {
  const UserProfile({
    required this.userId,
    required this.profileCompleted,
    this.id,
    this.firstName,
    this.lastName,
    this.displayName,
    this.nationalId,
    this.birthDate,
    this.gender,
    this.provinceId,
    this.countyId,
    this.districtId,
    this.ruralDistrictId,
    this.cityId,
    this.villageId,
    this.address,
    this.postalCode,
    this.avatarFileId,
    this.avatarUrl,
    this.bio,
  });

  final int? id;
  final int userId;
  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? nationalId;
  final String? birthDate;
  final String? gender;
  final int? provinceId;
  final int? countyId;
  final int? districtId;
  final int? ruralDistrictId;
  final int? cityId;
  final int? villageId;
  final String? address;
  final String? postalCode;
  final String? avatarFileId;
  final String? avatarUrl;
  final String? bio;
  final bool profileCompleted;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] == null ? null : (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      firstName: json['first_name']?.toString(),
      lastName: json['last_name']?.toString(),
      displayName: json['display_name']?.toString(),
      nationalId: json['national_id']?.toString(),
      birthDate: json['birth_date']?.toString(),
      gender: json['gender']?.toString(),
      provinceId:
          json['province_id'] == null
              ? null
              : (json['province_id'] as num).toInt(),
      countyId:
          json['county_id'] == null ? null : (json['county_id'] as num).toInt(),
      districtId:
          json['district_id'] == null
              ? null
              : (json['district_id'] as num).toInt(),
      ruralDistrictId:
          json['rural_district_id'] == null
              ? null
              : (json['rural_district_id'] as num).toInt(),
      cityId: json['city_id'] == null ? null : (json['city_id'] as num).toInt(),
      villageId:
          json['village_id'] == null
              ? null
              : (json['village_id'] as num).toInt(),
      address: json['address']?.toString(),
      postalCode: json['postal_code']?.toString(),
      avatarFileId: json['avatar_file_id']?.toString(),
      avatarUrl: json['avatar_url']?.toString(),
      bio: json['bio']?.toString(),
      profileCompleted: json['profile_completed'] == true,
    );
  }
}

class ProfileUpdateInput {
  const ProfileUpdateInput({
    this.firstName,
    this.lastName,
    this.displayName,
    this.nationalId,
    this.birthDate,
    this.gender,
    this.provinceId,
    this.countyId,
    this.cityId,
    this.address,
    this.postalCode,
    this.avatarFileId,
    this.bio,
  });

  final String? firstName;
  final String? lastName;
  final String? displayName;
  final String? nationalId;
  final String? birthDate;
  final String? gender;
  final int? provinceId;
  final int? countyId;
  final int? cityId;
  final String? address;
  final String? postalCode;
  final String? avatarFileId;
  final String? bio;

  Map<String, dynamic> toJson() {
    return {
      'first_name': firstName,
      'last_name': lastName,
      'display_name': displayName,
      'national_id': nationalId,
      'birth_date': birthDate,
      'gender': gender,
      'province_id': provinceId,
      'county_id': countyId,
      'city_id': cityId,
      'address': address,
      'postal_code': postalCode,
      'avatar_file_id': avatarFileId,
      'bio': bio,
    };
  }
}
