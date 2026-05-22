import '../config/app_config.dart';

String? absoluteApiUrl(String? path) {
  if (path == null || path.isEmpty) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;

  final origin = AppConfig.apiBaseUrl.replaceFirst('/api/v1', '');
  return '$origin$path';
}
