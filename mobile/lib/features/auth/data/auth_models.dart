class AuthUser {
  const AuthUser({
    required this.id,
    required this.status,
    required this.isEmailVerified,
    required this.isPhoneVerified,
    this.email,
    this.phone,
    this.roles = const [],
    this.permissions = const [],
  });

  final int id;
  final String? email;
  final String? phone;
  final String status;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final List<String> roles;
  final List<String> permissions;

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: (json['id'] as num).toInt(),
      email: json['email']?.toString(),
      phone: json['phone']?.toString(),
      status: json['status']?.toString() ?? 'unknown',
      isEmailVerified: json['is_email_verified'] == true,
      isPhoneVerified: json['is_phone_verified'] == true,
      roles:
          (json['roles'] as List?)?.map((item) => item.toString()).toList() ??
          [],
      permissions:
          (json['permissions'] as List?)
              ?.map((item) => item.toString())
              .toList() ??
          [],
    );
  }
}

class AuthTokenPair {
  const AuthTokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.user,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final AuthUser user;

  factory AuthTokenPair.fromJson(Map<String, dynamic> json) {
    return AuthTokenPair(
      accessToken: json['access_token'].toString(),
      refreshToken: json['refresh_token'].toString(),
      tokenType: json['token_type']?.toString() ?? 'bearer',
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}

class OtpRequestResult {
  const OtpRequestResult({
    required this.phone,
    required this.expiresInSeconds,
    this.devCode,
  });

  final String phone;
  final int expiresInSeconds;
  final String? devCode;

  factory OtpRequestResult.fromJson(Map<String, dynamic> json) {
    return OtpRequestResult(
      phone: json['phone'].toString(),
      expiresInSeconds: (json['expires_in_seconds'] as num).toInt(),
      devCode: json['dev_code']?.toString(),
    );
  }
}
