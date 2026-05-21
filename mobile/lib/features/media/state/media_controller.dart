import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/media_api.dart';
import '../data/media_models.dart';
import '../data/media_repository.dart';
import 'media_state.dart';

final mediaControllerProvider =
    StateNotifierProvider<MediaController, MediaState>((ref) {
      return MediaController(repository: ref.watch(mediaRepositoryProvider));
    });

class MediaController extends StateNotifier<MediaState> {
  MediaController({required MediaRepository repository})
    : _repository = repository,
      super(MediaState.initial());

  final MediaRepository _repository;

  Future<MediaFileModel?> pickAndUpload({
    required String purpose,
    required String visibility,
    String? altText,
    String? description,
    FileType fileType = FileType.custom,
    List<String> allowedExtensions = const [
      'jpg',
      'jpeg',
      'png',
      'webp',
      'pdf',
    ],
  }) async {
    state = state.copyWith(
      isUploading: true,
      clearError: true,
      clearLastUploaded: true,
    );

    try {
      final result = await FilePicker.platform.pickFiles(
        type: fileType,
        allowedExtensions: allowedExtensions,
        withData: true,
      );

      if (result == null || result.files.isEmpty) {
        state = state.copyWith(isUploading: false);
        return null;
      }

      final uploaded = await _repository.uploadPlatformFile(
        file: result.files.first,
        purpose: purpose,
        visibility: visibility,
        altText: altText,
        description: description,
      );

      state = state.copyWith(isUploading: false, lastUploaded: uploaded);
      return uploaded;
    } on MediaApiException catch (error) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: error.error.message,
      );
      return null;
    } catch (_) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: 'خطا در آپلود فایل',
      );
      return null;
    }
  }

  Future<void> loadMyMedia({String? purpose, String? visibility}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final items = await _repository.listMyMedia(
        purpose: purpose,
        visibility: visibility,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on MediaApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت فایل‌ها',
      );
    }
  }

  Future<bool> deleteMedia(String fileKey) async {
    state = state.copyWith(isUploading: true, clearError: true);

    try {
      await _repository.deleteMedia(fileKey);
      final items =
          state.items.where((item) => item.fileKey != fileKey).toList();

      state = state.copyWith(isUploading: false, items: items);
      return true;
    } on MediaApiException catch (error) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: 'خطا در حذف فایل',
      );
      return false;
    }
  }
}
