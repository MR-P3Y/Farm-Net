class MediaFileModel {
  const MediaFileModel({
    required this.id,
    required this.fileKey,
    required this.originalFilename,
    required this.storedFilename,
    required this.relativePath,
    required this.storageDisk,
    required this.mimeType,
    required this.extension,
    required this.sizeBytes,
    required this.checksumSha256,
    required this.visibility,
    required this.status,
    required this.purpose,
    required this.createdAt,
    required this.updatedAt,
    this.ownerUserId,
    this.width,
    this.height,
    this.altText,
    this.description,
    this.deletedAt,
  });

  final int id;
  final int? ownerUserId;
  final String fileKey;
  final String originalFilename;
  final String storedFilename;
  final String relativePath;
  final String storageDisk;
  final String mimeType;
  final String extension;
  final int sizeBytes;
  final String checksumSha256;
  final String visibility;
  final String status;
  final String purpose;
  final int? width;
  final int? height;
  final String? altText;
  final String? description;
  final String createdAt;
  final String updatedAt;
  final String? deletedAt;

  String? get publicUrl {
    if (visibility != 'public' || status != 'active') return null;
    return '/api/v1/media/public/$fileKey';
  }

  String? get privateUrl {
    if (visibility != 'private' || status != 'active') return null;
    return '/api/v1/media/private/$fileKey';
  }

  factory MediaFileModel.fromJson(Map<String, dynamic> json) {
    return MediaFileModel(
      id: (json['id'] as num).toInt(),
      ownerUserId:
          json['owner_user_id'] == null
              ? null
              : (json['owner_user_id'] as num).toInt(),
      fileKey: json['file_key']?.toString() ?? '',
      originalFilename: json['original_filename']?.toString() ?? '',
      storedFilename: json['stored_filename']?.toString() ?? '',
      relativePath: json['relative_path']?.toString() ?? '',
      storageDisk: json['storage_disk']?.toString() ?? '',
      mimeType: json['mime_type']?.toString() ?? '',
      extension: json['extension']?.toString() ?? '',
      sizeBytes: (json['size_bytes'] as num?)?.toInt() ?? 0,
      checksumSha256: json['checksum_sha256']?.toString() ?? '',
      visibility: json['visibility']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      purpose: json['purpose']?.toString() ?? '',
      width: json['width'] == null ? null : (json['width'] as num).toInt(),
      height: json['height'] == null ? null : (json['height'] as num).toInt(),
      altText: json['alt_text']?.toString(),
      description: json['description']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
      deletedAt: json['deleted_at']?.toString(),
    );
  }
}
