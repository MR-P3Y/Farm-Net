import 'package:farm_net_admin/core/storage/admin_token_storage.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
    SharedPreferences.setMockInitialValues({});
  });

  test('admin tokens are stored outside shared preferences', () async {
    final storage = AdminTokenStorage();
    await storage.saveTokens(
      accessToken: 'secure-access',
      refreshToken: 'secure-refresh',
    );

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('admin_access_token'), isNull);
    expect(prefs.getString('admin_refresh_token'), isNull);
    expect(await storage.getAccessToken(), 'secure-access');
    expect(await storage.getRefreshToken(), 'secure-refresh');
  });

  test('legacy admin tokens migrate once and are erased', () async {
    SharedPreferences.setMockInitialValues({
      'admin_access_token': 'legacy-access',
      'admin_refresh_token': 'legacy-refresh',
    });
    final storage = AdminTokenStorage();

    expect(await storage.getAccessToken(), 'legacy-access');
    expect(await storage.getRefreshToken(), 'legacy-refresh');

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('admin_access_token'), isNull);
    expect(prefs.getString('admin_refresh_token'), isNull);
  });

  test('clear removes secure and legacy admin token copies', () async {
    final storage = AdminTokenStorage();
    await storage.saveTokens(
      accessToken: 'secure-access',
      refreshToken: 'secure-refresh',
    );
    await storage.clear();

    expect(await storage.getAccessToken(), isNull);
    expect(await storage.getRefreshToken(), isNull);
  });
}
