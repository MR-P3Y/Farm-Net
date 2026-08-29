import 'package:dio/dio.dart';
import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_service_models.dart';

class AdminServiceApiException implements Exception {
  const AdminServiceApiException(this.error);
  final AdminApiError error;
}

class AdminServiceApi {
  AdminServiceApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokens = tokenStorage ?? AdminTokenStorage();
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
      throw AdminServiceApiException(
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

  Future<List<AdminServiceCategory>> categories({String? q}) async {
    final json = await _call(
      'GET',
      _query('/admin/services/categories', {'q': q}),
    );
    return (json['data'] as List? ?? const [])
        .map((e) => AdminServiceCategory.fromJson((e as Map).cast()))
        .toList();
  }

  Future<void> saveCategory({
    int? id,
    required Map<String, dynamic> data,
  }) async => _call(
    id == null ? 'POST' : 'PATCH',
    id == null
        ? '/admin/services/categories'
        : '/admin/services/categories/$id',
    data: data,
  );
  Future<AdminServicePage<AdminServiceProvider>> providers({
    int page = 1,
    String? status,
    String? q,
  }) async => AdminServicePage.fromJson(
    await _call(
      'GET',
      _query('/admin/services/provider-profiles', {
        'page': page,
        'page_size': 20,
        'status': status,
        'q': q,
      }),
    ),
    AdminServiceProvider.fromJson,
  );
  Future<void> providerStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/services/provider-profiles/$id/status',
    data: {'status': status, 'note': note},
  );
  Future<AdminServicePage<AdminServiceOffer>> offers({
    int page = 1,
    String? status,
    String? q,
  }) async => AdminServicePage.fromJson(
    await _call(
      'GET',
      _query('/admin/services/offers', {
        'page': page,
        'page_size': 20,
        'status': status,
        'q': q,
      }),
    ),
    AdminServiceOffer.fromJson,
  );
  Future<void> offerStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/services/offers/$id/status',
    data: {'status': status, 'note': note},
  );
  Future<AdminServicePage<AdminServiceRequest>> requests({
    int page = 1,
    String? status,
  }) async => AdminServicePage.fromJson(
    await _call(
      'GET',
      _query('/admin/services/requests', {
        'page': page,
        'page_size': 20,
        'status': status,
      }),
    ),
    AdminServiceRequest.fromJson,
  );
  Future<AdminServiceRequest> requestDetail(int id) async =>
      AdminServiceRequest.fromJson(
        ((await _call('GET', '/admin/services/requests/$id'))['data'] as Map)
            .cast(),
      );
  Future<void> requestStatus(int id, String status, String? note) => _call(
    'PATCH',
    '/admin/services/requests/$id/status',
    data: {'status': status, 'note': note},
  );
  Future<void> confirmRequestCompletion(int id) => _call(
    'POST',
    '/admin/services/requests/$id/confirm-completion',
    data: const {},
  );
}
