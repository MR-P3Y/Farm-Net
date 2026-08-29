import '../data/auth_models.dart';

class AuthState {
  const AuthState({
    required this.isLoading,
    required this.isAuthenticated,
    this.user,
    this.errorMessage,
    this.errorCode,
    this.errorDetails = const {},
    this.errorTraceId,
    this.devOtpCode,
    this.pendingPhone,
  });

  final bool isLoading;
  final bool isAuthenticated;
  final AuthUser? user;
  final String? errorMessage;
  final String? errorCode;
  final Map<String, dynamic> errorDetails;
  final String? errorTraceId;
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
    String? errorCode,
    Map<String, dynamic>? errorDetails,
    String? errorTraceId,
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
      errorCode: clearError ? null : errorCode ?? this.errorCode,
      errorDetails: clearError ? const {} : errorDetails ?? this.errorDetails,
      errorTraceId: clearError ? null : errorTraceId ?? this.errorTraceId,
      devOtpCode: clearDevOtp ? null : devOtpCode ?? this.devOtpCode,
      pendingPhone: pendingPhone ?? this.pendingPhone,
    );
  }

  AuthState unauthenticated() {
    return const AuthState(isLoading: false, isAuthenticated: false);
  }
}
