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

  String get displayName => email ?? phone ?? 'کاربر فارم‌نت';

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

class PasswordResetRequestResult {
  const PasswordResetRequestResult({
    required this.expiresInSeconds,
    this.devCode,
  });

  final int expiresInSeconds;
  final String? devCode;

  factory PasswordResetRequestResult.fromJson(Map<String, dynamic> json) {
    return PasswordResetRequestResult(
      expiresInSeconds: (json['expires_in_seconds'] as num?)?.toInt() ?? 0,
      devCode: json['dev_code'] as String?,
    );
  }
}

class EmailRegistrationInput {
  const EmailRegistrationInput({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    required this.nationalId,
    required this.provinceId,
    required this.countyId,
    required this.address,
    this.displayName,
    this.cityId,
    this.postalCode,
  });

  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final String? displayName;
  final String nationalId;
  final int provinceId;
  final int countyId;
  final int? cityId;
  final String address;
  final String? postalCode;

  Map<String, dynamic> toJson() => {
    'email': email,
    'password': password,
    'first_name': firstName,
    'last_name': lastName,
    if (displayName?.isNotEmpty == true) 'display_name': displayName,
    'national_id': nationalId,
    'province_id': provinceId,
    'county_id': countyId,
    if (cityId != null) 'city_id': cityId,
    'address': address,
    if (postalCode?.isNotEmpty == true) 'postal_code': postalCode,
  };
}

class AuthSessionModel {
  const AuthSessionModel({
    required this.id,
    required this.status,
    required this.isCurrent,
    required this.createdAt,
    this.ipAddress,
    this.userAgent,
    this.lastSeenAt,
    this.expiresAt,
  });

  final int id;
  final String status;
  final String? ipAddress;
  final String? userAgent;
  final bool isCurrent;
  final String createdAt;
  final String? lastSeenAt;
  final String? expiresAt;

  factory AuthSessionModel.fromJson(Map<String, dynamic> json) {
    return AuthSessionModel(
      id: (json['id'] as num).toInt(),
      status: json['status']?.toString() ?? 'unknown',
      ipAddress: json['ip_address']?.toString(),
      userAgent: json['user_agent']?.toString(),
      isCurrent: json['is_current'] == true,
      createdAt: json['created_at']?.toString() ?? '',
      lastSeenAt: json['last_seen_at']?.toString(),
      expiresAt: json['expires_at']?.toString(),
    );
  }
}
