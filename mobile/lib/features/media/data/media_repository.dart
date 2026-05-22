import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'media_api.dart';
import 'media_models.dart';

final mediaRepositoryProvider = Provider<MediaRepository>((ref) {
  return MediaRepository(api: MediaApi());
});

class MediaRepository {
  MediaRepository({required MediaApi api}) : _api = api;

  final MediaApi _api;

  Future<MediaFileModel> uploadPlatformFile({
    required PlatformFile file,
    required String purpose,
    required String visibility,
    String? altText,
    String? description,
  }) {
    return _api.uploadPlatformFile(
      file: file,
      purpose: purpose,
      visibility: visibility,
      altText: altText,
      description: description,
    );
  }

  Future<List<MediaFileModel>> listMyMedia({
    String? purpose,
    String? visibility,
  }) {
    return _api.listMyMedia(purpose: purpose, visibility: visibility);
  }

  Future<MediaFileModel> deleteMedia(String fileKey) {
    return _api.deleteMedia(fileKey);
  }
}
