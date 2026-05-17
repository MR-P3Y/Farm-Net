import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_verification_api.dart';
import 'admin_verification_models.dart';

final adminVerificationRepositoryProvider =
    Provider<AdminVerificationRepository>((ref) {
      return AdminVerificationRepository(api: AdminVerificationApi());
    });

class AdminVerificationRepository {
  AdminVerificationRepository({required AdminVerificationApi api}) : _api = api;

  final AdminVerificationApi _api;

  Future<List<AdminVerificationRequest>> listVerifications({
    int page = 1,
    int pageSize = 20,
    String? status,
    String? targetRole,
  }) {
    return _api.listVerifications(
      page: page,
      pageSize: pageSize,
      status: status,
      targetRole: targetRole,
    );
  }

  Future<AdminVerificationRequest> getDetail(int requestId) {
    return _api.getDetail(requestId);
  }

  Future<AdminVerificationRequest> updateStatus({
    required int requestId,
    required String status,
    String? note,
  }) {
    return _api.updateStatus(requestId: requestId, status: status, note: note);
  }
}
