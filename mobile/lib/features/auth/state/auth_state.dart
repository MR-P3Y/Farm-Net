import '../data/auth_models.dart';

class AuthState {
  const AuthState({
    required this.isLoading,
    required this.isAuthenticated,
    this.user,
    this.errorMessage,
    this.devOtpCode,
    this.pendingPhone,
  });

  final bool isLoading;
  final bool isAuthenticated;
  final AuthUser? user;
  final String? errorMessage;
  final String? devOtpCode;
  final String? pendingPhone;

  factory AuthState.initial() {
    return const AuthState(isLoading: true, isAuthenticated: false);
  }

  AuthState copyWith({
    bool? isLoading,
    bool? isAuthenticated,
    AuthUser? user,
    String? errorMessage,
    String? devOtpCode,
    String? pendingPhone,
    bool clearError = false,
    bool clearDevOtp = false,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      user: user ?? this.user,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
      devOtpCode: clearDevOtp ? null : devOtpCode ?? this.devOtpCode,
      pendingPhone: pendingPhone ?? this.pendingPhone,
    );
  }

  AuthState unauthenticated() {
    return const AuthState(isLoading: false, isAuthenticated: false);
  }
}
