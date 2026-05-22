import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_media_api.dart';
import 'admin_media_models.dart';

final adminMediaRepositoryProvider = Provider<AdminMediaRepository>((ref) {
  return AdminMediaRepository(api: AdminMediaApi());
});

class AdminMediaRepository {
  AdminMediaRepository({required AdminMediaApi api}) : _api = api;

  final AdminMediaApi _api;

  Future<List<AdminMediaFile>> listMedia({
    String? purpose,
    String? visibility,
    String? status,
  }) {
    return _api.listMedia(
      purpose: purpose,
      visibility: visibility,
      status: status,
    );
  }

  Future<AdminMediaFile> getMedia(String fileKey) {
    return _api.getMedia(fileKey);
  }

  Future<AdminMediaFile> updateStatus({
    required String fileKey,
    required String status,
    String? description,
  }) {
    return _api.updateStatus(
      fileKey: fileKey,
      status: status,
      description: description,
    );
  }
}
