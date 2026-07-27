import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'barzegar_api.dart';
import 'barzegar_models.dart';

final barzegarRepositoryProvider = Provider<BarzegarRepository>(
  (ref) => BarzegarRepository(BarzegarApi()),
);

class BarzegarRepository {
  const BarzegarRepository(this._api);
  final BarzegarApi _api;

  Future<List<BarzegarConversation>> conversations() => _api.conversations();
  Future<BarzegarConversation> createConversation() =>
      _api.createConversation();
  Future<BarzegarConversation> conversation(int id) => _api.conversation(id);
  Future<BarzegarRequest> request(int id) => _api.request(id);
  Future<List<BarzegarDiarySuggestion>> diarySuggestions() =>
      _api.diarySuggestions();
  Future<List<BarzegarFarmerReport>> reports() => _api.reports();

  Future<BarzegarRequest> submit({
    required int conversationId,
    required String content,
    required BarzegarFeature feature,
    int? contextConsentId,
    String? mediaFileKey,
  }) => _api.submit(
    conversationId: conversationId,
    content: content,
    feature: feature,
    contextConsentId: contextConsentId,
    mediaFileKey: mediaFileKey,
  );

  Future<BarzegarContextConsent> createConsent({
    required int farmId,
    required int? plotId,
    required int? cycleId,
    required String purpose,
  }) => _api.createConsent(
    farmId: farmId,
    plotId: plotId,
    cycleId: cycleId,
    purpose: purpose,
  );

  Future<BarzegarDiarySuggestion> decideSuggestion(
    int id, {
    required bool accept,
    String? reason,
  }) => _api.decideSuggestion(id, accept: accept, reason: reason);
}
