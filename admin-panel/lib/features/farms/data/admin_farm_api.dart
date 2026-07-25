import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_farm_models.dart';

class AdminFarmApiException implements Exception {
  const AdminFarmApiException(this.error);
  final AdminApiError error;
}

class AdminFarmApi {
  AdminFarmApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokens = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokens;

  Future<AdminFarmPage> list({
    String? query,
    String? status,
    int page = 1,
  }) async {
    final json = await _get(
      '/admin/farms',
      query: {
        if (query != null && query.isNotEmpty) 'q': query,
        if (status != null && status.isNotEmpty) 'status': status,
        'page': page,
        'page_size': 20,
      },
    );
    final meta = (json['meta'] as Map).cast<String, dynamic>();
    return AdminFarmPage(
      items:
          (json['data'] as List)
              .map((e) => AdminFarmSummary.fromJson((e as Map).cast()))
              .toList(),
      page: (meta['page'] as num).toInt(),
      total: (meta['total'] as num).toInt(),
      totalPages: (meta['total_pages'] as num).toInt(),
    );
  }

  Future<AdminFarmDetail> detail(int farmId) async {
    final json = await _get('/admin/farms/$farmId');
    return AdminFarmDetail.fromJson((json['data'] as Map).cast());
  }

  Future<List<AdminFarmAudit>> audit(int farmId) async {
    final json = await _get('/admin/farms/$farmId/audit');
    return (json['data'] as List)
        .map((e) => AdminFarmAudit.fromJson((e as Map).cast()))
        .toList();
  }

  Future<Map<String, dynamic>> _get(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    _client.setToken(await _tokens.getAccessToken());
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        path,
        queryParameters: query,
      );
      return response.data ?? <String, dynamic>{};
    } on DioException catch (error) {
      final data = error.response?.data;
      throw AdminFarmApiException(
        data is Map<String, dynamic>
            ? AdminApiError.fromJson(data)
            : AdminApiError(
              code: 'NETWORK_ERROR',
              message: error.message ?? 'Network error',
            ),
      );
    }
  }
}
