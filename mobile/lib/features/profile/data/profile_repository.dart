import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'profile_api.dart';
import 'profile_models.dart';

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(api: ProfileApi());
});

class ProfileRepository {
  ProfileRepository({required ProfileApi api}) : _api = api;

  final ProfileApi _api;

  Future<UserProfile> getMe() {
    return _api.getMe();
  }

  Future<UserProfile> updateMe(ProfileUpdateInput input) {
    return _api.updateMe(input);
  }
}
