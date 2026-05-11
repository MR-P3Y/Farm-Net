import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'verification_api.dart';
import 'verification_models.dart';

final verificationRepositoryProvider = Provider<VerificationRepository>((ref) {
  return VerificationRepository(api: VerificationApi());
});

class VerificationRepository {
  VerificationRepository({required VerificationApi api}) : _api = api;

  final VerificationApi _api;

  Future<List<VerificationRequest>> listMine() {
    return _api.listMine();
  }

  Future<VerificationRequest> create(VerificationCreateInput input) {
    return _api.create(input);
  }

  Future<VerificationRequest> attachDocument({
    required int requestId,
    required int documentId,
  }) {
    return _api.attachDocument(requestId: requestId, documentId: documentId);
  }

  Future<VerificationRequest> submit({required int requestId}) {
    return _api.submit(requestId: requestId);
  }
}
