class UserDocument {
  const UserDocument({
    required this.id,
    required this.userId,
    required this.documentType,
    required this.filePath,
    required this.fileName,
    required this.status,
    required this.uploadedAt,
    required this.createdAt,
    required this.updatedAt,
    this.mimeType,
    this.sizeBytes,
    this.reviewedAt,
    this.reviewedBy,
    this.rejectReason,
  });

  final int id;
  final int userId;
  final String documentType;
  final String filePath;
  final String fileName;
  final String? mimeType;
  final int? sizeBytes;
  final String status;
  final String uploadedAt;
  final String? reviewedAt;
  final int? reviewedBy;
  final String? rejectReason;
  final String createdAt;
  final String updatedAt;

  factory UserDocument.fromJson(Map<String, dynamic> json) {
    return UserDocument(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      documentType: json['document_type']?.toString() ?? '',
      filePath: json['file_path']?.toString() ?? '',
      fileName: json['file_name']?.toString() ?? '',
      mimeType: json['mime_type']?.toString(),
      sizeBytes:
          json['size_bytes'] == null
              ? null
              : (json['size_bytes'] as num).toInt(),
      status: json['status']?.toString() ?? '',
      uploadedAt: json['uploaded_at']?.toString() ?? '',
      reviewedAt: json['reviewed_at']?.toString(),
      reviewedBy:
          json['reviewed_by'] == null
              ? null
              : (json['reviewed_by'] as num).toInt(),
      rejectReason: json['reject_reason']?.toString(),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class DocumentCreateInput {
  const DocumentCreateInput({
    required this.documentType,
    required this.filePath,
    required this.fileName,
    this.mimeType,
    this.sizeBytes,
  });

  final String documentType;
  final String filePath;
  final String fileName;
  final String? mimeType;
  final int? sizeBytes;

  Map<String, dynamic> toJson() {
    return {
      'document_type': documentType,
      'file_path': filePath,
      'file_name': fileName,
      'mime_type': mimeType,
      'size_bytes': sizeBytes,
    };
  }
}
