import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_finance_models.dart';

class AdminFinanceApiException implements Exception {
  const AdminFinanceApiException(this.error);
  final AdminApiError error;
}

class AdminFinanceApi {
  AdminFinanceApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokens = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokens;

  Future<AdminFinancePageResult> list(
    AdminFinanceResource resource, {
    required int page,
  }) async {
    _client.setToken(await _tokens.getAccessToken());
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/admin/finance/${resource.path}',
        queryParameters: {'page': page, 'page_size': 20},
      );
      final json = response.data ?? const <String, dynamic>{};
      final rows =
          (json['data'] as List? ?? const [])
              .map(
                (item) => AdminFinanceRecord.fromJson(
                  resource,
                  (item as Map).cast<String, dynamic>(),
                ),
              )
              .toList();
      final meta = (json['meta'] as Map?)?.cast<String, dynamic>() ?? const {};
      return AdminFinancePageResult(
        items: rows,
        page: (meta['page'] as num?)?.toInt() ?? page,
        totalPages: (meta['total_pages'] as num?)?.toInt() ?? 0,
        total: (meta['total'] as num?)?.toInt() ?? rows.length,
      );
    } on DioException catch (error) {
      final data = error.response?.data;
      throw AdminFinanceApiException(
        data is Map
            ? AdminApiError.fromJson(data.cast<String, dynamic>())
            : AdminApiError(
              code: 'NETWORK_ERROR',
              message: error.message ?? 'Network error',
            ),
      );
    }
  }
}
