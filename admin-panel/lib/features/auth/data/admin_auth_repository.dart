import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/storage/admin_token_storage.dart';
import 'admin_auth_api.dart';
import 'admin_auth_models.dart';

final adminAuthRepositoryProvider = Provider<AdminAuthRepository>((ref) {
  return AdminAuthRepository(
    api: AdminAuthApi(),
    tokenStorage: AdminTokenStorage(),
  );
});

class AdminAuthRepository {
  AdminAuthRepository({
    required AdminAuthApi api,
    required AdminTokenStorage tokenStorage,
  }) : _api = api,
       _tokenStorage = tokenStorage;

  final AdminAuthApi _api;
  final AdminTokenStorage _tokenStorage;

  Future<AdminTokenPair> loginWithEmail({
    required String email,
    required String password,
  }) async {
    final result = await _api.loginWithEmail(email: email, password: password);

    await _saveTokenPair(result);
    return result;
  }

  Future<AdminAuthUser?> loadCurrentUser() async {
    final accessToken = await _tokenStorage.getAccessToken();

    if (accessToken == null || accessToken.isEmpty) {
      return null;
    }

    _api.setToken(accessToken);

    try {
      return await _api.me();
    } on AdminAuthApiException {
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

  Future<AdminTokenPair?> _tryRefresh() async {
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

  Future<void> _saveTokenPair(AdminTokenPair pair) async {
    await _tokenStorage.saveTokens(
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
    );

    _api.setToken(pair.accessToken);
  }
}
