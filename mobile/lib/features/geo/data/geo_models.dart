class GeoProvince {
  const GeoProvince({
    required this.id,
    required this.name,
    required this.amarCode,
  });

  final int id;
  final String name;
  final String amarCode;

  factory GeoProvince.fromJson(Map<String, dynamic> json) {
    return GeoProvince(
      id: (json['id'] as num).toInt(),
      name: json['name']?.toString() ?? '',
      amarCode: json['amar_code']?.toString() ?? '',
    );
  }
}

class GeoCounty {
  const GeoCounty({
    required this.id,
    required this.provinceId,
    required this.name,
    required this.amarCode,
  });

  final int id;
  final int provinceId;
  final String name;
  final String amarCode;

  factory GeoCounty.fromJson(Map<String, dynamic> json) {
    return GeoCounty(
      id: (json['id'] as num).toInt(),
      provinceId: (json['province_id'] as num).toInt(),
      name: json['name']?.toString() ?? '',
      amarCode: json['amar_code']?.toString() ?? '',
    );
  }
}

class GeoCity {
  const GeoCity({
    required this.id,
    required this.provinceId,
    required this.countyId,
    required this.name,
    required this.amarCode,
    this.districtId,
    this.cityType,
  });

  final int id;
  final int provinceId;
  final int countyId;
  final int? districtId;
  final String name;
  final String? cityType;
  final String amarCode;

  factory GeoCity.fromJson(Map<String, dynamic> json) {
    return GeoCity(
      id: (json['id'] as num).toInt(),
      provinceId: (json['province_id'] as num).toInt(),
      countyId: (json['county_id'] as num).toInt(),
      districtId:
          json['district_id'] == null
              ? null
              : (json['district_id'] as num).toInt(),
      name: json['name']?.toString() ?? '',
      cityType: json['city_type']?.toString(),
      amarCode: json['amar_code']?.toString() ?? '',
    );
  }
}
