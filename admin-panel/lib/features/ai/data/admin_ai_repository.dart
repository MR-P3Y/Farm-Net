import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_ai_api.dart';
import 'admin_ai_models.dart';

final adminAIRepositoryProvider = Provider(
  (ref) => AdminAIRepository(AdminAIApi()),
);

class AdminAIRepository {
  const AdminAIRepository(this._api);
  final AdminAIApi _api;

  Future<AdminAIOverview> overview() => _api.overview();
  Future<List<AdminAIRequest>> requests({String? status}) =>
      _api.requests(status: status);
  Future<List<AdminAIKnowledgeSource>> sources() => _api.sources();
  Future<List<AdminAIUsage>> usage() => _api.usage();
  Future<List<AdminAIPolicy>> policies() => _api.policies();
  Future<AdminAIKnowledgeSource> createSource(Map<String, dynamic> data) =>
      _api.createSource(data);
  Future<AdminAIKnowledgeSource> submitSource(int id) => _api.submitSource(id);
  Future<AdminAIKnowledgeSource> reviewSource(
    int id, {
    required String decision,
    required String reason,
  }) => _api.reviewSource(id, decision: decision, reason: reason);
}
