import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_consultant_api.dart';
import 'admin_consultant_models.dart';

final adminConsultantRepositoryProvider = Provider<AdminConsultantRepository>((
  ref,
) {
  return AdminConsultantRepository(api: AdminConsultantApi());
});

class AdminConsultantRepository {
  AdminConsultantRepository({required AdminConsultantApi api}) : _api = api;

  final AdminConsultantApi _api;

  Future<List<AdminConsultSpecialty>> listSpecialties() =>
      _api.listSpecialties();

  Future<AdminConsultSpecialty> createSpecialty({
    required String code,
    required String title,
    String? description,
    required int sortOrder,
    required bool isActive,
  }) {
    return _api.createSpecialty(
      code: code,
      title: title,
      description: description,
      sortOrder: sortOrder,
      isActive: isActive,
    );
  }

  Future<AdminConsultSpecialty> updateSpecialty({
    required int id,
    required String code,
    required String title,
    String? description,
    required int sortOrder,
    required bool isActive,
  }) {
    return _api.updateSpecialty(
      id: id,
      code: code,
      title: title,
      description: description,
      sortOrder: sortOrder,
      isActive: isActive,
    );
  }

  Future<List<AdminConsultProfile>> listProfiles({String? status}) =>
      _api.listProfiles(status: status);

  Future<AdminConsultProfile> updateProfileStatus({
    required int id,
    required String status,
    String? note,
  }) {
    return _api.updateProfileStatus(id: id, status: status, note: note);
  }

  Future<List<AdminConsultRequest>> listRequests({String? status}) =>
      _api.listRequests(status: status);

  Future<AdminConsultRequest> requestDetail(int id) {
    return _api.requestDetail(id);
  }

  Future<AdminConsultRequest> updateRequestStatus({
    required int id,
    required String status,
    String? note,
  }) {
    return _api.updateRequestStatus(id: id, status: status, note: note);
  }
}
