import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/storage/token_storage.dart';
import 'auth_api.dart';
import 'auth_models.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(api: AuthApi(), tokenStorage: TokenStorage());
});

class AuthRepository {
  AuthRepository({required AuthApi api, required TokenStorage tokenStorage})
    : _api = api,
      _tokenStorage = tokenStorage;

  final AuthApi _api;
  final TokenStorage _tokenStorage;

  Future<AuthTokenPair> registerWithEmail(EmailRegistrationInput input) async {
    final result = await _api.registerWithEmail(input);

    await _saveTokenPair(result);
    return result;
  }

  Future<AuthTokenPair> loginWithEmail({
    required String email,
    required String password,
  }) async {
    final result = await _api.loginWithEmail(email: email, password: password);

    await _saveTokenPair(result);
    return result;
  }

  Future<OtpRequestResult> requestOtp({required String phone}) {
    return _api.requestOtp(phone: phone);
  }

  Future<AuthTokenPair> verifyOtp({
    required String phone,
    required String code,
  }) async {
    final result = await _api.verifyOtp(phone: phone, code: code);

    await _saveTokenPair(result);
    return result;
  }

  Future<AuthUser?> loadCurrentUser() async {
    final accessToken = await _tokenStorage.getAccessToken();

    if (accessToken == null || accessToken.isEmpty) {
      return null;
    }

    _api.setToken(accessToken);

    try {
      return await _api.me();
    } on AuthApiException {
      final refreshed = await _tryRefresh();

      if (refreshed == null) {
        await _tokenStorage.clear();
        _api.setToken(null);
        return null;
      }

      _api.setToken(refreshed.accessToken);
      return refreshed.user;
    }
  }

  Future<void> logout() async {
    final refreshToken = await _tokenStorage.getRefreshToken();

    try {
      await _api.logout(refreshToken: refreshToken);
    } catch (_) {
      // Local logout must still happen if backend logout fails.
    }

    await _tokenStorage.clear();
    _api.setToken(null);
  }

  Future<List<AuthSessionModel>> listSessions() => _api.listSessions();

  Future<void> revokeSession(int sessionId) => _api.revokeSession(sessionId);

  Future<int> revokeOtherSessions() => _api.revokeOtherSessions();

  Future<int> changePassword({
    required String currentPassword,
    required String newPassword,
  }) => _api.changePassword(
    currentPassword: currentPassword,
    newPassword: newPassword,
  );

  Future<PasswordResetRequestResult> requestPasswordReset({
    required String identifier,
  }) => _api.requestPasswordReset(identifier: identifier);

  Future<int> confirmPasswordReset({
    required String identifier,
    required String code,
    required String newPassword,
  }) => _api.confirmPasswordReset(
    identifier: identifier,
    code: code,
    newPassword: newPassword,
  );

  Future<AuthTokenPair?> _tryRefresh() async {
    final refreshToken = await _tokenStorage.getRefreshToken();

    if (refreshToken == null || refreshToken.isEmpty) {
      return null;
    }

    try {
      final result = await _api.refresh(refreshToken: refreshToken);
      await _saveTokenPair(result);
      return result;
    } catch (_) {
      return null;
    }
  }

  Future<void> _saveTokenPair(AuthTokenPair pair) async {
    await _tokenStorage.saveTokens(
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
    );

    _api.setToken(pair.accessToken);
  }
}
