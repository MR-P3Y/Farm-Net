import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/auth_api.dart';
import '../data/auth_models.dart';
import '../data/auth_repository.dart';
import 'auth_state.dart';

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>(
  (ref) {
    return AuthController(repository: ref.watch(authRepositoryProvider));
  },
);

class AuthController extends StateNotifier<AuthState> {
  AuthController({required AuthRepository repository})
    : _repository = repository,
      super(AuthState.initial());

  final AuthRepository _repository;

  Future<void> loadCurrentUser() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final user = await _repository.loadCurrentUser();

      if (user == null) {
        state = state.unauthenticated();
        return;
      }

      state = AuthState(isLoading: false, isAuthenticated: true, user: user);
    } catch (_) {
      state = const AuthState(
        isLoading: false,
        isAuthenticated: false,
        errorMessage: 'خطا در بررسی وضعیت ورود',
      );
    }
  }

  Future<bool> loginWithEmail({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await _repository.loginWithEmail(
        email: email,
        password: password,
      );

      state = AuthState(
        isLoading: false,
        isAuthenticated: true,
        user: result.user,
      );

      return true;
    } on AuthApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: false,
        errorMessage: error.error.message,
        errorCode: error.error.code,
        errorDetails: error.error.details,
        errorTraceId: error.error.traceId,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: false,
        errorMessage: 'خطای ارتباط با سرور',
        errorCode: 'NETWORK_ERROR',
      );
      return false;
    }
  }

  Future<bool> registerWithEmail(EmailRegistrationInput input) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await _repository.registerWithEmail(input);

      state = AuthState(
        isLoading: false,
        isAuthenticated: true,
        user: result.user,
      );

      return true;
    } on AuthApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: false,
        errorMessage: error.error.message,
        errorCode: error.error.code,
        errorDetails: error.error.details,
        errorTraceId: error.error.traceId,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: false,
        errorMessage: 'خطای ارتباط با سرور',
        errorCode: 'NETWORK_ERROR',
      );
      return false;
    }
  }

  Future<bool> requestOtp({required String phone}) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearDevOtp: true,
    );

    try {
      final result = await _repository.requestOtp(phone: phone);

      state = state.copyWith(
        isLoading: false,
        pendingPhone: result.phone,
        devOtpCode: result.devCode,
      );

      return true;
    } on AuthApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
        errorCode: error.error.code,
        errorDetails: error.error.details,
        errorTraceId: error.error.traceId,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطای ارتباط با سرور',
        errorCode: 'NETWORK_ERROR',
      );
      return false;
    }
  }

  Future<bool> verifyOtp({required String phone, required String code}) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await _repository.verifyOtp(phone: phone, code: code);

      state = AuthState(
        isLoading: false,
        isAuthenticated: true,
        user: result.user,
      );

      return true;
    } on AuthApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
        errorCode: error.error.code,
        errorDetails: error.error.details,
        errorTraceId: error.error.traceId,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطای ارتباط با سرور',
        errorCode: 'NETWORK_ERROR',
      );
      return false;
    }
  }

  Future<void> logout() async {
    state = state.copyWith(isLoading: true, clearError: true);

    await _repository.logout();

    state = state.unauthenticated();
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }
}
