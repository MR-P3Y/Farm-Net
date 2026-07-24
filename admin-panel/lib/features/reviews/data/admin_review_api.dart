import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_review_models.dart';

class AdminReviewApiException implements Exception {
  const AdminReviewApiException(this.error);
  final AdminApiError error;
}

class AdminReviewApi {
  AdminReviewApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokens = tokenStorage ?? AdminTokenStorage();
  final AdminApiClient _client;
  final AdminTokenStorage _tokens;

  Future<AdminReviewPage<AdminReview>> reviews({
    String? status,
    int page = 1,
  }) async {
    final json = await _get('/admin/reviews', status: status, page: page);
    return _page(
      json,
      (item) => AdminReview.fromJson(item),
    );
  }

  Future<AdminReviewPage<AdminReviewReport>> reports({
    String? status,
    int page = 1,
  }) async {
    final json = await _get(
      '/admin/reviews/reports',
      status: status,
      page: page,
    );
    return _page(json, (item) => AdminReviewReport.fromJson(item));
  }

  Future<List<AdminReviewLog>> logs(int reviewId) async {
    final json = await _get('/admin/reviews/$reviewId/moderation-logs');
    return (json['data'] as List? ?? const [])
        .map((e) => AdminReviewLog.fromJson((e as Map).cast()))
        .toList();
  }

  Future<void> moderateReview(int id, String status, String note) =>
      _patch('/admin/reviews/$id/status', {'status': status, 'note': note});

  Future<void> resolveReport(int id, String status, String note) => _patch(
    '/admin/reviews/reports/$id/status',
    {'status': status, 'resolution_note': note},
  );

  Future<Map<String, dynamic>> _get(
    String path, {
    String? status,
    int? page,
  }) async {
    await _auth();
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        path,
        queryParameters: {
          if (status != null) 'status': status,
          if (page != null) 'page': page,
          if (page != null) 'page_size': 20,
        },
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminReviewApiException(_error(error));
    }
  }

  Future<void> _patch(String path, Map<String, dynamic> data) async {
    await _auth();
    try {
      await _client.dio.patch(path, data: data);
    } on DioException catch (error) {
      throw AdminReviewApiException(_error(error));
    }
  }

  Future<void> _auth() async => _client.setToken(await _tokens.getAccessToken());

  AdminReviewPage<T> _page<T>(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) parse,
  ) {
    final meta = (json['meta'] as Map?)?.cast<String, dynamic>() ?? {};
    return AdminReviewPage(
      items: (json['data'] as List? ?? const [])
          .map((e) => parse((e as Map).cast<String, dynamic>()))
          .toList(),
      page: (meta['page'] as num?)?.toInt() ?? 1,
      total: (meta['total'] as num?)?.toInt() ?? 0,
      totalPages: (meta['total_pages'] as num?)?.toInt() ?? 0,
    );
  }

  AdminApiError _error(DioException error) {
    final data = error.response?.data;
    return data is Map<String, dynamic>
        ? AdminApiError.fromJson(data)
        : AdminApiError(
            code: 'NETWORK_ERROR',
            message: error.message ?? 'Network error',
          );
  }
}
