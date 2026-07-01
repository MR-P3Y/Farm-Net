import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'consultant_api.dart';
import 'consultant_models.dart';

final consultantRepositoryProvider = Provider<ConsultantRepository>((ref) {
  return ConsultantRepository(api: ConsultantApi());
});

class ConsultantRepository {
  const ConsultantRepository({required ConsultantApi api}) : _api = api;

  final ConsultantApi _api;

  Future<List<ConsultantSpecialtyModel>> specialties() {
    return _api.specialties();
  }

  Future<List<ConsultantProfileModel>> list({
    int? specialtyId,
    String? query,
    int page = 1,
    int pageSize = 20,
  }) {
    return _api.list(
      specialtyId: specialtyId,
      query: query,
      page: page,
      pageSize: pageSize,
    );
  }

  Future<ConsultantProfileModel> detail(int profileId) {
    return _api.detail(profileId);
  }
}
