import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/auth_api.dart';
import '../data/auth_models.dart';
import '../data/auth_repository.dart';

final accountSecurityControllerProvider = StateNotifierProvider.autoDispose<
  AccountSecurityController,
  AccountSecurityState
>((ref) {
  return AccountSecurityController(
    repository: ref.watch(authRepositoryProvider),
  );
});

class AccountSecurityState {
  const AccountSecurityState({
    this.isLoading = false,
    this.isSaving = false,
    this.sessions = const [],
    this.errorCode,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AuthSessionModel> sessions;
  final String? errorCode;

  AccountSecurityState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AuthSessionModel>? sessions,
    String? errorCode,
    bool clearError = false,
  }) {
    return AccountSecurityState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      sessions: sessions ?? this.sessions,
      errorCode: clearError ? null : errorCode ?? this.errorCode,
    );
  }
}

class AccountSecurityController extends StateNotifier<AccountSecurityState> {
  AccountSecurityController({required AuthRepository repository})
    : _repository = repository,
      super(const AccountSecurityState());

  final AuthRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final sessions = await _repository.listSessions();
      state = state.copyWith(isLoading: false, sessions: sessions);
    } on AuthApiException catch (error) {
      state = state.copyWith(isLoading: false, errorCode: error.error.code);
    } catch (_) {
      state = state.copyWith(isLoading: false, errorCode: 'NETWORK_ERROR');
    }
  }

  Future<bool> revokeSession(int sessionId) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      await _repository.revokeSession(sessionId);
      state = state.copyWith(
        isSaving: false,
        sessions:
            state.sessions.where((session) => session.id != sessionId).toList(),
      );
      return true;
    } on AuthApiException catch (error) {
      state = state.copyWith(isSaving: false, errorCode: error.error.code);
      return false;
    } catch (_) {
      state = state.copyWith(isSaving: false, errorCode: 'NETWORK_ERROR');
      return false;
    }
  }

  Future<int?> revokeOtherSessions() async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final count = await _repository.revokeOtherSessions();
      state = state.copyWith(
        isSaving: false,
        sessions: state.sessions.where((session) => session.isCurrent).toList(),
      );
      return count;
    } on AuthApiException catch (error) {
      state = state.copyWith(isSaving: false, errorCode: error.error.code);
      return null;
    } catch (_) {
      state = state.copyWith(isSaving: false, errorCode: 'NETWORK_ERROR');
      return null;
    }
  }

  Future<int?> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final count = await _repository.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
      );
      state = state.copyWith(isSaving: false);
      await load();
      return count;
    } on AuthApiException catch (error) {
      state = state.copyWith(isSaving: false, errorCode: error.error.code);
      return null;
    } catch (_) {
      state = state.copyWith(isSaving: false, errorCode: 'NETWORK_ERROR');
      return null;
    }
  }
}
