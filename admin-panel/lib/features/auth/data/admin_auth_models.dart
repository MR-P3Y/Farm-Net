class AdminAuthUser {
  const AdminAuthUser({
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

  factory AdminAuthUser.fromJson(Map<String, dynamic> json) {
    return AdminAuthUser(
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

  bool hasPermission(String permission) {
    return permissions.contains(permission);
  }
}

class AdminTokenPair {
  const AdminTokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.user,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final AdminAuthUser user;

  factory AdminTokenPair.fromJson(Map<String, dynamic> json) {
    return AdminTokenPair(
      accessToken: json['access_token'].toString(),
      refreshToken: json['refresh_token'].toString(),
      tokenType: json['token_type']?.toString() ?? 'bearer',
      user: AdminAuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}
