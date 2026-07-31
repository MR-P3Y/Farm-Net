import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'barzegar_models.dart';

class BarzegarApiException implements Exception {
  const BarzegarApiException(this.error);
  final ApiError error;

  @override
  String toString() => error.message;
}

class BarzegarApi {
  BarzegarApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<BarzegarConversation>> conversations() async {
    final json = await _get('ai/conversations');
    return _list(json, BarzegarConversation.fromJson);
  }

  Future<BarzegarConversation> createConversation() async {
    final json = await _post('ai/conversations', {'title': 'گفت‌وگو با برزگر'});
    return BarzegarConversation.fromJson(_data(json));
  }

  Future<BarzegarConversation> conversation(int id) async {
    final json = await _get('ai/conversations/$id');
    return BarzegarConversation.fromJson(_data(json));
  }

  Future<BarzegarRequest> submit({
    required int conversationId,
    required String content,
    required BarzegarFeature feature,
    int? contextConsentId,
    String? mediaFileKey,
  }) async {
    final json = await _post('ai/conversations/$conversationId/requests', {
      'idempotency_key':
          'mobile-${DateTime.now().microsecondsSinceEpoch}-$conversationId',
      'content': content,
      'feature_code': feature.featureCode,
      'request_kind': feature.requestKind,
      if (contextConsentId != null) 'context_consent_id': contextConsentId,
      if (mediaFileKey != null) 'media_file_key': mediaFileKey,
    });
    return BarzegarRequest.fromJson(_data(json));
  }

  Future<BarzegarRequest> request(int id) async {
    final json = await _get('ai/requests/$id');
    return BarzegarRequest.fromJson(_data(json));
  }

  Future<void> submitFeedback(int requestId, {required bool helpful}) async {
    await _post('ai/requests/$requestId/feedback', {
      'rating': helpful ? 'helpful' : 'not_helpful',
      'reason_codes': <String>[],
      'comment': null,
    });
  }

  Future<void> requestConversationDeletion(int conversationId) async {
    await _post('ai/conversations/$conversationId/deletion-requests', {
      'idempotency_key':
          'mobile-delete-${DateTime.now().microsecondsSinceEpoch}-$conversationId',
    });
  }

  Future<BarzegarContextConsent> createConsent({
    required int farmId,
    required int? plotId,
    required int? cycleId,
    required String purpose,
  }) async {
    final json = await _post('ai/context-consents', {
      'idempotency_key':
          'mobile-consent-${DateTime.now().microsecondsSinceEpoch}-$farmId',
      'farm_id': farmId,
      'plot_id': plotId,
      'crop_cycle_id': cycleId,
      'purpose': purpose,
      'expires_in_hours': 24,
    });
    return BarzegarContextConsent.fromJson(_data(json));
  }

  Future<List<BarzegarDiarySuggestion>> diarySuggestions() async {
    final json = await _get('ai/diary-suggestions');
    return _list(json, BarzegarDiarySuggestion.fromJson);
  }

  Future<BarzegarDiarySuggestion> decideSuggestion(
    int id, {
    required bool accept,
    String? reason,
  }) async {
    final json = await _post(
      'ai/diary-suggestions/$id/${accept ? 'accept' : 'reject'}',
      {'reason': reason},
    );
    return BarzegarDiarySuggestion.fromJson(_data(json));
  }

  Future<List<BarzegarFarmerReport>> reports() async {
    final json = await _get('ai/farmer-reports');
    return _list(json, BarzegarFarmerReport.fromJson);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.get(path);
      return (response.data as Map).cast<String, dynamic>();
    } on DioException catch (error) {
      throw BarzegarApiException(_error(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.post(path, data: data);
      return (response.data as Map).cast<String, dynamic>();
    } on DioException catch (error) {
      throw BarzegarApiException(_error(error));
    }
  }

  Map<String, dynamic> _data(Map<String, dynamic> json) =>
      (json['data'] as Map).cast<String, dynamic>();

  List<T> _list<T>(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) parser,
  ) =>
      (json['data'] as List? ?? const [])
          .whereType<Map>()
          .map((item) => parser(item.cast<String, dynamic>()))
          .toList();

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map) return ApiError.fromJson(data.cast<String, dynamic>());
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'خطا در ارتباط با سرور',
    );
  }
}
