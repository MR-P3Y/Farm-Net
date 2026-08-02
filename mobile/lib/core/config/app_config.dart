class AppConfig {
  const AppConfig._();

  static const appName = 'Farm Net';
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );
  static const mapTileUrl = String.fromEnvironment(
    'MAP_TILE_URL',
    defaultValue: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  );
  static const mapUserAgent = String.fromEnvironment(
    'MAP_USER_AGENT',
    defaultValue: 'FarmNet/0.26 (+https://farmnet.ir)',
  );
  static const requestTimeout = Duration(seconds: 30);
}
