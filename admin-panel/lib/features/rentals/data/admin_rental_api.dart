import 'package:dio/dio.dart';
import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_rental_models.dart';

class AdminRentalApiException implements Exception {
  const AdminRentalApiException(this.error);
  final AdminApiError error;
}

class AdminRentalApi {
  AdminRentalApi({AdminApiClient? client, AdminTokenStorage? tokens})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokens = tokens ?? AdminTokenStorage();
  final AdminApiClient _client;
  final AdminTokenStorage _tokens;
  Future<Map<String, dynamic>> _call(
    String method,
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      _client.setToken(await _tokens.getAccessToken());
      final r = await _client.dio.request<Map<String, dynamic>>(
        path,
        data: data,
        options: Options(method: method),
      );
      return r.data ?? {};
    } on DioException catch (e) {
      final d = e.response?.data;
      throw AdminRentalApiException(
        d is Map<String, dynamic>
            ? AdminApiError.fromJson(d)
            : AdminApiError(
              code: 'NETWORK_ERROR',
              message: e.message ?? 'Network error',
            ),
      );
    }
  }

  String _query(String path, Map<String, dynamic> q) {
    q.removeWhere((k, v) => v == null || v == '');
    return Uri(
      path: path,
      queryParameters: q.map((k, v) => MapEntry(k, '$v')),
    ).toString();
  }

  Future<List<AdminRentalCategory>> categories() async {
    final j = await _call('GET', '/admin/rentals/categories');
    return (j['data'] as List? ?? const [])
        .map((e) => AdminRentalCategory.fromJson((e as Map).cast()))
        .toList();
  }

  Future<void> saveCategory(int? id, Map<String, dynamic> data) => _call(
    id == null ? 'POST' : 'PATCH',
    id == null ? '/admin/rentals/categories' : '/admin/rentals/categories/$id',
    data: data,
  );
  Future<AdminRentalPage<AdminLessorProfile>> profiles({
    int page = 1,
    String? status,
  }) async => AdminRentalPage.fromJson(
    await _call(
      'GET',
      _query('/admin/rentals/lessor-profiles', {
        'page': page,
        'page_size': 20,
        'status': status,
      }),
    ),
    AdminLessorProfile.fromJson,
  );
  Future<void> profileStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/rentals/lessor-profiles/$id/status',
    data: {'status': status, 'admin_note': note},
  );
  Future<AdminRentalPage<AdminRentalEquipment>> equipment({
    int page = 1,
    String? status,
  }) async => AdminRentalPage.fromJson(
    await _call(
      'GET',
      _query('/admin/rentals/equipment', {
        'page': page,
        'page_size': 20,
        'status': status,
      }),
    ),
    AdminRentalEquipment.fromJson,
  );
  Future<void> equipmentStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/rentals/equipment/$id/status',
    data: {'status': status, 'admin_note': note},
  );
  Future<AdminRentalPage<AdminRentalRequest>> requests({
    int page = 1,
    String? status,
  }) async => AdminRentalPage.fromJson(
    await _call(
      'GET',
      _query('/admin/rentals/requests', {
        'page': page,
        'page_size': 20,
        'status': status,
      }),
    ),
    AdminRentalRequest.fromJson,
  );
  Future<AdminRentalRequest> requestDetail(int id) async =>
      AdminRentalRequest.fromJson(
        ((await _call('GET', '/admin/rentals/requests/$id'))['data'] as Map)
            .cast(),
      );
  Future<void> requestStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/rentals/requests/$id/status',
    data: {'status': status, 'note': note},
  );
}
