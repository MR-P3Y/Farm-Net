import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_social_models.dart';

class AdminSocialApiException implements Exception {
  const AdminSocialApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminSocialApi {
  AdminSocialApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminSocialReport>> reports({
    String? status,
    String? targetType,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (targetType != null && targetType.isNotEmpty) {
      query['target_type'] = targetType;
    }

    final uri = Uri(path: '/admin/social/reports', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => AdminSocialReport.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AdminSocialReport> updateReportStatus({
    required int reportId,
    required String status,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/social/reports/$reportId/status',
      data: {'status': status},
    );

    return AdminSocialReport.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<AdminSocialPost>> posts({
    String? status,
    String? postType,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (postType != null && postType.isNotEmpty) query['post_type'] = postType;

    final uri = Uri(path: '/admin/social/posts', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map((item) => AdminSocialPost.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AdminSocialPost> hidePost({
    required int postId,
    String? reason,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/social/posts/$postId/hide',
      data: {'reason': reason},
    );

    return AdminSocialPost.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminSocialPost> unhidePost({
    required int postId,
    String? reason,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/social/posts/$postId/unhide',
      data: {'reason': reason},
    );

    return AdminSocialPost.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<AdminSocialComment>> comments({
    String? status,
    int? postId,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (postId != null) query['post_id'] = postId.toString();

    final uri = Uri(path: '/admin/social/comments', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => AdminSocialComment.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminSocialComment> hideComment({
    required int commentId,
    String? reason,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/social/comments/$commentId/hide',
      data: {'reason': reason},
    );

    return AdminSocialComment.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminSocialComment> unhideComment({
    required int commentId,
    String? reason,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/social/comments/$commentId/unhide',
      data: {'reason': reason},
    );

    return AdminSocialComment.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminSocialApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminSocialApiException(_mapDioError(error));
    }
  }

  AdminApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map<String, dynamic>) {
      return AdminApiError.fromJson(data);
    }

    return AdminApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
