class SearchResultItem {
  const SearchResultItem({
    required this.type,
    required this.resourceId,
    required this.title,
    required this.route,
    this.subtitle,
    this.imageUrl,
    this.provinceId,
    this.cityId,
    this.price,
    this.currency,
    this.rating,
  });

  final String type;
  final int resourceId;
  final String title;
  final String route;
  final String? subtitle;
  final String? imageUrl;
  final int? provinceId;
  final int? cityId;
  final num? price;
  final String? currency;
  final num? rating;

  factory SearchResultItem.fromJson(Map<String, dynamic> json) =>
      SearchResultItem(
        type: json['type']?.toString() ?? '',
        resourceId: (json['resource_id'] as num?)?.toInt() ?? 0,
        title: json['title']?.toString() ?? '',
        route: json['route']?.toString() ?? '',
        subtitle: json['subtitle']?.toString(),
        imageUrl: json['image_url']?.toString(),
        provinceId: (json['province_id'] as num?)?.toInt(),
        cityId: (json['city_id'] as num?)?.toInt(),
        price: _number(json['price']),
        currency: json['currency']?.toString(),
        rating: _number(json['rating']),
      );

  static num? _number(Object? value) =>
      value is num ? value : num.tryParse(value?.toString() ?? '');
}

class SearchResultGroup {
  const SearchResultGroup({
    required this.type,
    required this.items,
    required this.total,
  });
  final String type;
  final List<SearchResultItem> items;
  final int total;

  factory SearchResultGroup.fromJson(Map<String, dynamic> json) =>
      SearchResultGroup(
        type: json['type']?.toString() ?? '',
        items:
            (json['items'] as List? ?? const [])
                .whereType<Map<String, dynamic>>()
                .map(SearchResultItem.fromJson)
                .toList(),
        total: (json['total'] as num?)?.toInt() ?? 0,
      );
}

class UnifiedSearchResult {
  const UnifiedSearchResult({
    required this.query,
    required this.groups,
    required this.total,
  });
  final String query;
  final List<SearchResultGroup> groups;
  final int total;

  factory UnifiedSearchResult.fromJson(Map<String, dynamic> json) =>
      UnifiedSearchResult(
        query: json['query']?.toString() ?? '',
        groups:
            (json['groups'] as List? ?? const [])
                .whereType<Map<String, dynamic>>()
                .map(SearchResultGroup.fromJson)
                .toList(),
        total: (json['total'] as num?)?.toInt() ?? 0,
      );
}

const searchResultTypes = <String>[
  'product',
  'store',
  'service',
  'rental_equipment',
  'consultant',
  'social_post',
];

const searchTypeLabels = <String, String>{
  'product': 'محصولات',
  'store': 'فروشگاه‌ها',
  'service': 'خدمات',
  'rental_equipment': 'تجهیزات اجاره‌ای',
  'consultant': 'مشاوران',
  'social_post': 'جامعه کشاورزی',
};
