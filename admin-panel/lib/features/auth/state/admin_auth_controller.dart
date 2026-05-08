import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/admin_auth_state.dart';
import '../data/admin_auth_api.dart';
import '../data/admin_auth_repository.dart';

final adminAuthControllerProvider = Provider<AdminAuthController>((ref) {
  return AdminAuthController(ref);
});

class AdminAuthController {
  AdminAuthController(this._ref);

  final Ref _ref;

  AdminAuthRepository get _repository => _ref.read(adminAuthRepositoryProvider);

  AdminAuthStateController get _state =>
      _ref.read(adminAuthStateProvider.notifier);

  Future<void> loadCurrentUser() async {
    _state.setLoading();

    try {
      final user = await _repository.loadCurrentUser();

      if (user == null) {
        _state.setUnauthenticated();
        return;
      }

      _state.setAuthenticated(user);
    } catch (_) {
      _state.setUnauthenticated();
    }
  }

  Future<bool> loginWithEmail({
    required String email,
    required String password,
  }) async {
    _state.setLoading();

    try {
      final result = await _repository.loginWithEmail(
        email: email,
        password: password,
      );

      _state.setAuthenticated(result.user);
      return true;
    } on AdminAuthApiException catch (error) {
      _state.setError(error.error.message);
      return false;
    } catch (_) {
      _state.setError('خطای ارتباط با سرور');
      return false;
    }
  }

  Future<void> logout() async {
    _state.setLoading();

    await _repository.logout();

    _state.setUnauthenticated();
  }
}
