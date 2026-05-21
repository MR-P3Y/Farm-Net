import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'media_models.dart';

class MediaApiException implements Exception {
  const MediaApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class MediaApi {
  MediaApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<MediaFileModel> uploadPlatformFile({
    required PlatformFile file,
    required String purpose,
    required String visibility,
    String? altText,
    String? description,
  }) async {
    await _setStoredToken();

    if (file.bytes == null) {
      throw const MediaApiException(
        ApiError(
          code: 'FILE_BYTES_MISSING',
          message: 'فایل انتخاب‌شده قابل خواندن نیست.',
        ),
      );
    }

    final formData = FormData.fromMap({
      'purpose': purpose,
      'visibility': visibility,
      if (altText != null && altText.trim().isNotEmpty)
        'alt_text': altText.trim(),
      if (description != null && description.trim().isNotEmpty)
        'description': description.trim(),
      'file': MultipartFile.fromBytes(
        file.bytes!,
        filename: file.name,
        contentType: _mediaTypeFromFile(file),
      ),
    });

    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/media/upload',
        data: formData,
      );

      final json = response.data ?? {};
      return MediaFileModel.fromJson(json['data'] as Map<String, dynamic>);
    } on DioException catch (error) {
      throw MediaApiException(_mapDioError(error));
    }
  }

  Future<List<MediaFileModel>> listMyMedia({
    String? purpose,
    String? visibility,
  }) async {
    await _setStoredToken();

    final query = <String, String>{};
    if (purpose != null && purpose.isNotEmpty) query['purpose'] = purpose;
    if (visibility != null && visibility.isNotEmpty) {
      query['visibility'] = visibility;
    }

    final uri = Uri(
      path: '/media/me',
      queryParameters: query.isEmpty ? null : query,
    );

    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        uri.toString(),
      );

      final json = response.data ?? {};
      final rows = json['data'] as List? ?? [];

      return rows
          .map((item) => MediaFileModel.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (error) {
      throw MediaApiException(_mapDioError(error));
    }
  }

  Future<MediaFileModel> deleteMedia(String fileKey) async {
    await _setStoredToken();

    try {
      final response = await _client.dio.delete<Map<String, dynamic>>(
        '/media/$fileKey',
      );

      final json = response.data ?? {};
      return MediaFileModel.fromJson(json['data'] as Map<String, dynamic>);
    } on DioException catch (error) {
      throw MediaApiException(_mapDioError(error));
    }
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  ApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }

  DioMediaType? _mediaTypeFromFile(PlatformFile file) {
    final extension = file.extension?.toLowerCase();

    if (extension == 'jpg' || extension == 'jpeg') {
      return DioMediaType('image', 'jpeg');
    }
    if (extension == 'png') return DioMediaType('image', 'png');
    if (extension == 'webp') return DioMediaType('image', 'webp');
    if (extension == 'pdf') return DioMediaType('application', 'pdf');

    return null;
  }
}
