class AppConfig {
  const AppConfig._();

  static const appName = 'Farm Net';
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );
  static const requestTimeout = Duration(seconds: 30);
}
