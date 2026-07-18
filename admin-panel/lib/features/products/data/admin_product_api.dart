import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_product_models.dart';

class AdminProductApiException implements Exception {
  const AdminProductApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminProductApi {
  AdminProductApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminProduct>> listProducts({
    int page = 1,
    int pageSize = 20,
    String? status,
    int? storeId,
    int? categoryId,
    String? q,
  }) async {
    await _setStoredToken();

    final query = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (storeId != null) query['store_id'] = storeId.toString();
    if (categoryId != null) query['category_id'] = categoryId.toString();
    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();

    final uri = Uri(path: '/admin/products', queryParameters: query);
    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => AdminProduct.fromJson((item as Map).cast()))
        .toList();
  }

  Future<List<AdminProductCategory>> listCategories({String? q}) async {
    await _setStoredToken();
    final uri = Uri(
      path: '/admin/products/categories',
      queryParameters: q == null || q.trim().isEmpty ? null : {'q': q.trim()},
    );
    final json = await _get(uri.toString());
    return (json['data'] as List? ?? const [])
        .map((item) => AdminProductCategory.fromJson((item as Map).cast()))
        .toList();
  }

  Future<AdminProductCategory> saveCategory({
    int? id,
    required Map<String, dynamic> data,
  }) async {
    await _setStoredToken();
    try {
      final response =
          id == null
              ? await _client.dio.post<Map<String, dynamic>>(
                '/admin/products/categories',
                data: data,
              )
              : await _client.dio.patch<Map<String, dynamic>>(
                '/admin/products/categories/$id',
                data: data,
              );
      return AdminProductCategory.fromJson(
        ((response.data ?? {})['data'] as Map).cast(),
      );
    } on DioException catch (error) {
      throw AdminProductApiException(_mapDioError(error));
    }
  }

  Future<AdminProduct> getProductDetail(int productId) async {
    await _setStoredToken();

    final json = await _get('/admin/products/$productId');
    return AdminProduct.fromJson((json['data'] as Map).cast());
  }

  Future<AdminProduct> updateStatus({
    required int productId,
    required String status,
    String? note,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/products/$productId/status',
      data: {'status': status, 'note': note},
    );

    return AdminProduct.fromJson((json['data'] as Map).cast());
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
      throw AdminProductApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw AdminProductApiException(_mapDioError(error));
    }
  }

  AdminApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map) {
      return AdminApiError.fromJson(data.cast<String, dynamic>());
    }

    return AdminApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
