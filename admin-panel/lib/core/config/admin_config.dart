class AdminConfig {
  const AdminConfig._();

  static const appName = 'Farm Net Admin';
  static const apiBaseUrl = String.fromEnvironment(
    'ADMIN_API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1/admin',
  );
  static const requestTimeout = Duration(seconds: 15);
}
