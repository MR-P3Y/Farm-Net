import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_consultant_models.dart';

class AdminConsultantApiException implements Exception {
  const AdminConsultantApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminConsultantApi {
  AdminConsultantApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminConsultSpecialty>> listSpecialties() async {
    await _setStoredToken();

    final json = await _get('/admin/consultants/specialties');
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) =>
              AdminConsultSpecialty.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminConsultSpecialty> createSpecialty({
    required String code,
    required String title,
    String? description,
    required int sortOrder,
    required bool isActive,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/admin/consultants/specialties',
      data: {
        'code': code,
        'title': title,
        'description': description,
        'sort_order': sortOrder,
        'is_active': isActive,
      },
    );

    return AdminConsultSpecialty.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminConsultSpecialty> updateSpecialty({
    required int id,
    required String code,
    required String title,
    String? description,
    required int sortOrder,
    required bool isActive,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/consultants/specialties/$id',
      data: {
        'code': code,
        'title': title,
        'description': description,
        'sort_order': sortOrder,
        'is_active': isActive,
      },
    );

    return AdminConsultSpecialty.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<AdminConsultProfile>> listProfiles({String? status}) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};
    if (status != null && status.isNotEmpty) {
      query['status'] = status;
    }

    final uri = Uri(path: '/admin/consultants', queryParameters: query);
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => AdminConsultProfile.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminConsultProfile> updateProfileStatus({
    required int id,
    required String status,
    String? note,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/consultants/$id/status',
      data: {'status': status, 'note': note},
    );

    return AdminConsultProfile.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<AdminConsultRequest>> listRequests({String? status}) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};
    if (status != null && status.isNotEmpty) {
      query['status'] = status;
    }

    final uri = Uri(
      path: '/admin/consultants/requests',
      queryParameters: query,
    );
    final json = await _get(uri.toString());
    final rows = json['data'] as List? ?? [];

    return rows
        .map(
          (item) => AdminConsultRequest.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<AdminConsultRequest> requestDetail(int id) async {
    await _setStoredToken();

    final json = await _get('/admin/consultants/requests/$id');

    return AdminConsultRequest.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<AdminConsultRequest> updateRequestStatus({
    required int id,
    required String status,
    String? note,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/consultants/requests/$id/status',
      data: {'status': status, 'note': note},
    );

    return AdminConsultRequest.fromJson(json['data'] as Map<String, dynamic>);
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
      throw AdminConsultantApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminConsultantApiException(_mapDioError(error));
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
      throw AdminConsultantApiException(_mapDioError(error));
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
