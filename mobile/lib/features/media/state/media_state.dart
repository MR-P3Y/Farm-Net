import '../data/media_models.dart';

class MediaState {
  const MediaState({
    required this.isLoading,
    this.isUploading = false,
    this.items = const [],
    this.lastUploaded,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isUploading;
  final List<MediaFileModel> items;
  final MediaFileModel? lastUploaded;
  final String? errorMessage;

  factory MediaState.initial() {
    return const MediaState(isLoading: false);
  }

  MediaState copyWith({
    bool? isLoading,
    bool? isUploading,
    List<MediaFileModel>? items,
    MediaFileModel? lastUploaded,
    String? errorMessage,
    bool clearLastUploaded = false,
    bool clearError = false,
  }) {
    return MediaState(
      isLoading: isLoading ?? this.isLoading,
      isUploading: isUploading ?? this.isUploading,
      items: items ?? this.items,
      lastUploaded:
          clearLastUploaded ? null : lastUploaded ?? this.lastUploaded,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
