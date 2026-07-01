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

  Future<ConsultationRequestModel> createRequest({
    required int? consultantProfileId,
    required int? specialtyId,
    required String title,
    required String description,
    required String contactMethod,
  }) {
    return _api.createRequest(
      consultantProfileId: consultantProfileId,
      specialtyId: specialtyId,
      title: title,
      description: description,
      contactMethod: contactMethod,
    );
  }

  Future<List<ConsultationRequestModel>> myRequests({
    String? status,
    int page = 1,
    int pageSize = 50,
  }) {
    return _api.myRequests(status: status, page: page, pageSize: pageSize);
  }

  Future<ConsultationRequestModel> cancelRequest({
    required int requestId,
    String? note,
  }) {
    return _api.cancelRequest(requestId: requestId, note: note);
  }
}
