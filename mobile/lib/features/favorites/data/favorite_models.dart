enum FavoriteSubjectType {
  product('product'),
  store('store'),
  serviceOffer('service_offer'),
  rentalEquipment('rental_equipment'),
  consultant('consultant'),
  socialPost('social_post');

  const FavoriteSubjectType(this.apiValue);

  final String apiValue;
}

class FavoriteItem {
  const FavoriteItem({
    required this.id,
    required this.subjectType,
    required this.subjectId,
    required this.isAvailable,
    required this.createdAt,
    this.title,
    this.subtitle,
    this.imageUrl,
    this.route,
  });

  final int id;
  final FavoriteSubjectType subjectType;
  final int subjectId;
  final String? title;
  final String? subtitle;
  final String? imageUrl;
  final String? route;
  final bool isAvailable;
  final DateTime createdAt;

  factory FavoriteItem.fromJson(Map<String, dynamic> json) {
    return FavoriteItem(
      id: (json['id'] as num).toInt(),
      subjectType: FavoriteSubjectType.values.firstWhere(
        (item) => item.apiValue == json['subject_type'],
      ),
      subjectId: (json['subject_id'] as num).toInt(),
      title: json['title']?.toString(),
      subtitle: json['subtitle']?.toString(),
      imageUrl: json['image_url']?.toString(),
      route: json['route']?.toString(),
      isAvailable: json['is_available'] == true,
      createdAt: DateTime.parse(json['created_at'].toString()).toLocal(),
    );
  }
}
