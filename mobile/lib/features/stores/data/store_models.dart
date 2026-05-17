class Store {
  const Store({
    required this.id,
    required this.ownerUserId,
    required this.name,
    required this.slug,
    required this.storeType,
    required this.createdAt,
    required this.updatedAt,
    this.status,
    this.description,
    this.phone,
    this.email,
    this.provinceId,
    this.countyId,
    this.districtId,
    this.cityId,
    this.villageId,
    this.address,
    this.postalCode,
    this.latitude,
    this.longitude,
    this.logoFileId,
    this.bannerFileId,
    this.adminNote,
  });

  final int id;
  final int ownerUserId;
  final String name;
  final String slug;
  final String? status;
  final String storeType;
  final String? description;
  final String? phone;
  final String? email;
  final int? provinceId;
  final int? countyId;
  final int? districtId;
  final int? cityId;
  final int? villageId;
  final String? address;
  final String? postalCode;
  final String? latitude;
  final String? longitude;
  final String? logoFileId;
  final String? bannerFileId;
  final String? adminNote;
  final String createdAt;
  final String updatedAt;

  factory Store.fromJson(Map<String, dynamic> json) {
    return Store(
      id: (json['id'] as num).toInt(),
      ownerUserId: (json['owner_user_id'] as num).toInt(),
      name: json['name']?.toString() ?? '',
      slug: json['slug']?.toString() ?? '',
      status: json['status']?.toString(),
      storeType: json['store_type']?.toString() ?? 'other',
      description: json['description']?.toString(),
      phone: json['phone']?.toString(),
      email: json['email']?.toString(),
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
      cityId: json['city_id'] == null ? null : (json['city_id'] as num).toInt(),
      villageId:
          json['village_id'] == null
              ? null
              : (json['village_id'] as num).toInt(),
      address: json['address']?.toString(),
      postalCode: json['postal_code']?.toString(),
      latitude: json['latitude']?.toString(),
      longitude: json['longitude']?.toString(),
      logoFileId: json['logo_file_id']?.toString(),
      bannerFileId: json['banner_file_id']?.toString(),
      adminNote: json['admin_note']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class StoreCreateInput {
  const StoreCreateInput({
    required this.name,
    required this.slug,
    this.description,
    this.storeType = 'other',
    this.phone,
    this.email,
    this.provinceId,
    this.countyId,
    this.districtId,
    this.cityId,
    this.villageId,
    this.address,
    this.postalCode,
    this.latitude,
    this.longitude,
    this.logoFileId,
    this.bannerFileId,
  });

  final String name;
  final String slug;
  final String? description;
  final String storeType;
  final String? phone;
  final String? email;
  final int? provinceId;
  final int? countyId;
  final int? districtId;
  final int? cityId;
  final int? villageId;
  final String? address;
  final String? postalCode;
  final String? latitude;
  final String? longitude;
  final String? logoFileId;
  final String? bannerFileId;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'slug': slug,
      'description': description,
      'store_type': storeType,
      'phone': phone,
      'email': email,
      'province_id': provinceId,
      'county_id': countyId,
      'district_id': districtId,
      'city_id': cityId,
      'village_id': villageId,
      'address': address,
      'postal_code': postalCode,
      'latitude': latitude,
      'longitude': longitude,
      'logo_file_id': logoFileId,
      'banner_file_id': bannerFileId,
    };
  }
}

class StoreUpdateInput {
  const StoreUpdateInput({
    this.name,
    this.slug,
    this.description,
    this.storeType,
    this.phone,
    this.email,
    this.provinceId,
    this.countyId,
    this.districtId,
    this.cityId,
    this.villageId,
    this.address,
    this.postalCode,
    this.latitude,
    this.longitude,
    this.logoFileId,
    this.bannerFileId,
  });

  final String? name;
  final String? slug;
  final String? description;
  final String? storeType;
  final String? phone;
  final String? email;
  final int? provinceId;
  final int? countyId;
  final int? districtId;
  final int? cityId;
  final int? villageId;
  final String? address;
  final String? postalCode;
  final String? latitude;
  final String? longitude;
  final String? logoFileId;
  final String? bannerFileId;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'slug': slug,
      'description': description,
      'store_type': storeType,
      'phone': phone,
      'email': email,
      'province_id': provinceId,
      'county_id': countyId,
      'district_id': districtId,
      'city_id': cityId,
      'village_id': villageId,
      'address': address,
      'postal_code': postalCode,
      'latitude': latitude,
      'longitude': longitude,
      'logo_file_id': logoFileId,
      'banner_file_id': bannerFileId,
    };
  }
}
