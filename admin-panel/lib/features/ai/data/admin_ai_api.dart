import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import 'admin_ai_models.dart';

class AdminAIApiException implements Exception {
  const AdminAIApiException(this.error);
  final AdminApiError error;
  @override
  String toString() => error.message;
}

class AdminAIApi {
  AdminAIApi({AdminApiClient? client})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl);
  final AdminApiClient _client;

  Future<AdminAIOverview> overview() async =>
      AdminAIOverview.fromJson(_data(await _get('/admin/ai/overview')));

  Future<List<AdminAIRequest>> requests({String? status}) async => _list(
    await _get(
      '/admin/ai/requests',
      query: {'page': 1, 'page_size': 50, if (status != null) 'status': status},
    ),
    AdminAIRequest.fromJson,
  );

  Future<List<AdminAIKnowledgeSource>> sources() async => _list(
    await _get('/admin/ai/knowledge-sources'),
    AdminAIKnowledgeSource.fromJson,
  );

  Future<List<AdminAIUsage>> usage() async => _list(
    await _get('/admin/ai/usage', query: {'page': 1, 'page_size': 50}),
    AdminAIUsage.fromJson,
  );

  Future<List<AdminAIPolicy>> policies() async => _list(
    await _get('/admin/ai/policies'),
    AdminAIPolicy.fromJson,
  );

  Future<AdminAIKnowledgeSource> createSource(Map<String, dynamic> data) async =>
      AdminAIKnowledgeSource.fromJson(
        _data(await _post('/admin/ai/knowledge-sources', data)),
      );

  Future<AdminAIKnowledgeSource> submitSource(int id) async =>
      AdminAIKnowledgeSource.fromJson(
        _data(await _post('/admin/ai/knowledge-sources/$id/submit', {})),
      );

  Future<AdminAIKnowledgeSource> reviewSource(
    int id, {
    required String decision,
    required String reason,
  }) async => AdminAIKnowledgeSource.fromJson(
    _data(
      await _post('/admin/ai/knowledge-sources/$id/review', {
        'decision': decision,
        'reason': reason,
      }),
    ),
  );

  Future<Map<String, dynamic>> _get(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        path,
        queryParameters: query,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminAIApiException(_error(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminAIApiException(_error(error));
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

  AdminApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map) return AdminApiError.fromJson(data.cast<String, dynamic>());
    return AdminApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
    );
  }
}
