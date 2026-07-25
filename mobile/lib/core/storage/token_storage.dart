import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TokenStorage {
  TokenStorage({FlutterSecureStorage? secureStorage})
    : _secureStorage = secureStorage ?? const FlutterSecureStorage();

  static const _accessTokenKey = 'farmnet.auth.access_token.v1';
  static const _refreshTokenKey = 'farmnet.auth.refresh_token.v1';
  static const _legacyAccessTokenKey = 'access_token';
  static const _legacyRefreshTokenKey = 'refresh_token';

  final FlutterSecureStorage _secureStorage;

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
    await _secureStorage.write(key: _accessTokenKey, value: accessToken);
    await _clearLegacyTokens();
  }

  Future<String?> getAccessToken() async {
    return _readAndMigrate(
      secureKey: _accessTokenKey,
      legacyKey: _legacyAccessTokenKey,
    );
  }

  Future<String?> getRefreshToken() async {
    return _readAndMigrate(
      secureKey: _refreshTokenKey,
      legacyKey: _legacyRefreshTokenKey,
    );
  }

  Future<void> clear() async {
    await _secureStorage.delete(key: _accessTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
    await _clearLegacyTokens();
  }

  Future<String?> _readAndMigrate({
    required String secureKey,
    required String legacyKey,
  }) async {
    final secureValue = await _secureStorage.read(key: secureKey);
    if (secureValue != null && secureValue.isNotEmpty) {
      return secureValue;
    }

    final prefs = await SharedPreferences.getInstance();
    final legacyValue = prefs.getString(legacyKey);
    if (legacyValue == null || legacyValue.isEmpty) {
      return null;
    }

    await _secureStorage.write(key: secureKey, value: legacyValue);
    await prefs.remove(legacyKey);
    return legacyValue;
  }

  Future<void> _clearLegacyTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_legacyAccessTokenKey);
    await prefs.remove(_legacyRefreshTokenKey);
  }
}
