class ProductImage {
  const ProductImage({
    required this.id,
    required this.filePath,
    required this.sortOrder,
    required this.isPrimary,
    this.fileId,
    this.mediaFileId,
    this.fileKey,
    this.publicUrl,
    this.altText,
  });

  final int id;
  final String? fileId;
  final int? mediaFileId;
  final String? fileKey;
  final String? publicUrl;
  final String filePath;
  final String? altText;
  final int sortOrder;
  final bool isPrimary;

  factory ProductImage.fromJson(Map<String, dynamic> json) {
    return ProductImage(
      id: _asInt(json['id']),
      fileId: json['file_id']?.toString(),
      mediaFileId: _asNullableInt(json['media_file_id']),
      fileKey: json['file_key']?.toString(),
      publicUrl: json['public_url']?.toString(),
      filePath: json['file_path']?.toString() ?? '',
      altText: json['alt_text']?.toString(),
      sortOrder: _asInt(json['sort_order']),
      isPrimary: json['is_primary'] == true,
    );
  }
}

class ProductImageCreateInput {
  const ProductImageCreateInput({
    this.fileId,
    this.mediaFileKey,
    this.filePath,
    this.altText,
    this.sortOrder = 0,
    this.isPrimary = false,
  });

  final String? fileId;
  final String? mediaFileKey;
  final String? filePath;
  final String? altText;
  final int sortOrder;
  final bool isPrimary;

  Map<String, dynamic> toJson() {
    return {
      'file_id': fileId,
      'media_file_key': mediaFileKey,
      'file_path': filePath,
      'alt_text': altText,
      'sort_order': sortOrder,
      'is_primary': isPrimary,
    };
  }
}

class Product {
  const Product({
    required this.id,
    required this.storeId,
    required this.name,
    required this.slug,
    required this.price,
    required this.currency,
    required this.stockQuantity,
    required this.unit,
    required this.minOrderQuantity,
    required this.isFeatured,
    required this.createdAt,
    required this.updatedAt,
    this.storeName,
    this.storeSlug,
    this.categoryId,
    this.categoryName,
    this.categorySlug,
    this.shortDescription,
    this.description,
    this.sku,
    this.status,
    this.compareAtPrice,
    this.maxOrderQuantity,
    this.isActive = true,
    this.adminNote,
    this.primaryImage,
    this.images = const [],
  });

  final int id;
  final int storeId;
  final String? storeName;
  final String? storeSlug;
  final int? categoryId;
  final String? categoryName;
  final String? categorySlug;
  final String name;
  final String slug;
  final String? shortDescription;
  final String? description;
  final String? sku;
  final String? status;
  final num price;
  final num? compareAtPrice;
  final String currency;
  final int stockQuantity;
  final String unit;
  final int minOrderQuantity;
  final int? maxOrderQuantity;
  final bool isActive;
  final bool isFeatured;
  final String? adminNote;
  final ProductImage? primaryImage;
  final List<ProductImage> images;
  final String createdAt;
  final String updatedAt;

  factory Product.fromJson(Map<String, dynamic> json) {
    final imagesRaw = json['images'] as List? ?? [];
    final images =
        imagesRaw
            .map((item) => ProductImage.fromJson(item as Map<String, dynamic>))
            .toList();

    ProductImage? primaryImage;
    final primaryRaw = json['primary_image'];

    if (primaryRaw is Map<String, dynamic>) {
      primaryImage = ProductImage.fromJson(primaryRaw);
    } else {
      for (final image in images) {
        if (image.isPrimary) {
          primaryImage = image;
          break;
        }
      }
    }

    return Product(
      id: _asInt(json['id']),
      storeId: _asInt(json['store_id']),
      storeName: json['store_name']?.toString(),
      storeSlug: json['store_slug']?.toString(),
      categoryId: _asNullableInt(json['category_id']),
      categoryName: json['category_name']?.toString(),
      categorySlug: json['category_slug']?.toString(),
      name: json['name']?.toString() ?? '',
      slug: json['slug']?.toString() ?? '',
      shortDescription: json['short_description']?.toString(),
      description: json['description']?.toString(),
      sku: json['sku']?.toString(),
      status: json['status']?.toString(),
      price: _asNum(json['price']),
      compareAtPrice: _asNullableNum(json['compare_at_price']),
      currency: json['currency']?.toString() ?? 'TOMAN',
      stockQuantity: _asInt(json['stock_quantity']),
      unit: json['unit']?.toString() ?? 'piece',
      minOrderQuantity: _asInt(json['min_order_quantity'], fallback: 1),
      maxOrderQuantity: _asNullableInt(json['max_order_quantity']),
      isActive: json['is_active'] != false,
      isFeatured: json['is_featured'] == true,
      adminNote: json['admin_note']?.toString(),
      primaryImage: primaryImage,
      images: images,
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class ProductCreateInput {
  const ProductCreateInput({
    required this.name,
    required this.slug,
    required this.price,
    this.categoryId,
    this.shortDescription,
    this.description,
    this.sku,
    this.compareAtPrice,
    this.currency = 'TOMAN',
    this.stockQuantity = 0,
    this.unit = 'piece',
    this.minOrderQuantity = 1,
    this.maxOrderQuantity,
    this.isActive = true,
    this.isFeatured = false,
  });

  final int? categoryId;
  final String name;
  final String slug;
  final String? shortDescription;
  final String? description;
  final String? sku;
  final num price;
  final num? compareAtPrice;
  final String currency;
  final int stockQuantity;
  final String unit;
  final int minOrderQuantity;
  final int? maxOrderQuantity;
  final bool isActive;
  final bool isFeatured;

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'name': name,
      'slug': slug,
      'short_description': shortDescription,
      'description': description,
      'sku': sku,
      'price': price,
      'compare_at_price': compareAtPrice,
      'currency': currency,
      'stock_quantity': stockQuantity,
      'unit': unit,
      'min_order_quantity': minOrderQuantity,
      'max_order_quantity': maxOrderQuantity,
      'is_active': isActive,
      'is_featured': isFeatured,
    };
  }
}

class ProductUpdateInput {
  const ProductUpdateInput({
    this.categoryId,
    this.name,
    this.slug,
    this.shortDescription,
    this.description,
    this.sku,
    this.price,
    this.compareAtPrice,
    this.currency,
    this.stockQuantity,
    this.unit,
    this.minOrderQuantity,
    this.maxOrderQuantity,
    this.isActive,
    this.isFeatured,
  });

  final int? categoryId;
  final String? name;
  final String? slug;
  final String? shortDescription;
  final String? description;
  final String? sku;
  final num? price;
  final num? compareAtPrice;
  final String? currency;
  final int? stockQuantity;
  final String? unit;
  final int? minOrderQuantity;
  final int? maxOrderQuantity;
  final bool? isActive;
  final bool? isFeatured;

  Map<String, dynamic> toJson() {
    return {
      'category_id': categoryId,
      'name': name,
      'slug': slug,
      'short_description': shortDescription,
      'description': description,
      'sku': sku,
      'price': price,
      'compare_at_price': compareAtPrice,
      'currency': currency,
      'stock_quantity': stockQuantity,
      'unit': unit,
      'min_order_quantity': minOrderQuantity,
      'max_order_quantity': maxOrderQuantity,
      'is_active': isActive,
      'is_featured': isFeatured,
    };
  }
}

int _asInt(dynamic value, {int fallback = 0}) {
  if (value is num) return value.toInt();
  if (value is String) return int.tryParse(value) ?? fallback;
  return fallback;
}

int? _asNullableInt(dynamic value) {
  if (value == null) return null;
  return _asInt(value);
}

num _asNum(dynamic value, {num fallback = 0}) {
  if (value is num) return value;
  if (value is String) return num.tryParse(value) ?? fallback;
  return fallback;
}

num? _asNullableNum(dynamic value) {
  if (value == null) return null;
  return _asNum(value);
}
