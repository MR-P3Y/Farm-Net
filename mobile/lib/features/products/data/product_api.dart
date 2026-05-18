import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'product_models.dart';

class ProductApiException implements Exception {
  const ProductApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class ProductApi {
  ProductApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<List<Product>> listPublicProducts({
    String? q,
    int? storeId,
    int? categoryId,
    int? provinceId,
    int? countyId,
    int? cityId,
    String? storeType,
  }) async {
    final query = <String, String>{};

    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();
    if (storeId != null) query['store_id'] = storeId.toString();
    if (categoryId != null) query['category_id'] = categoryId.toString();
    if (provinceId != null) query['province_id'] = provinceId.toString();
    if (countyId != null) query['county_id'] = countyId.toString();
    if (cityId != null) query['city_id'] = cityId.toString();
    if (storeType != null && storeType.trim().isNotEmpty) {
      query['store_type'] = storeType.trim();
    }

    final uri = Uri(
      path: '/public/products',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Product.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Product> getPublicProductById(int productId) async {
    final json = await _get('/public/products/$productId');
    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<Product>> listPublicStoreProducts({
    required String storeSlug,
    String? q,
    int? categoryId,
  }) async {
    final query = <String, String>{};

    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();
    if (categoryId != null) query['category_id'] = categoryId.toString();

    final uri = Uri(
      path: '/public/stores/$storeSlug/products',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Product.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Product> getPublicStoreProductBySlug({
    required String storeSlug,
    required String productSlug,
  }) async {
    final json = await _get('/public/stores/$storeSlug/products/$productSlug');
    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<Product>> listMyProducts({
    required int storeId,
    String? status,
    int? categoryId,
    String? q,
  }) async {
    await _setStoredToken();

    final query = <String, String>{};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (categoryId != null) query['category_id'] = categoryId.toString();
    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();

    final uri = Uri(
      path: '/stores/$storeId/products/me',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Product.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Product> getMyProduct({
    required int storeId,
    required int productId,
  }) async {
    await _setStoredToken();

    final json = await _get('/stores/$storeId/products/$productId');
    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Product> createProduct({
    required int storeId,
    required ProductCreateInput input,
  }) async {
    await _setStoredToken();

    final json = await _post('/stores/$storeId/products', data: input.toJson());

    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Product> updateProduct({
    required int storeId,
    required int productId,
    required ProductUpdateInput input,
  }) async {
    await _setStoredToken();

    final json = await _put(
      '/stores/$storeId/products/$productId',
      data: input.toJson(),
    );

    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Product> publishProduct({
    required int storeId,
    required int productId,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/stores/$storeId/products/$productId/publish',
      data: {},
    );

    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Product> unpublishProduct({
    required int storeId,
    required int productId,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/stores/$storeId/products/$productId/unpublish',
      data: {},
    );

    return Product.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Product> archiveProduct({
    required int storeId,
    required int productId,
  }) async {
    await _setStoredToken();

    final json = await _delete('/stores/$storeId/products/$productId');
    return Product.fromJson(json['data'] as Map<String, dynamic>);
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
      throw ProductApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw ProductApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _put(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.dio.put<Map<String, dynamic>>(
        path,
        data: data,
      );
      return response.data ?? {};
    } on DioException catch (error) {
      throw ProductApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _delete(String path) async {
    try {
      final response = await _client.dio.delete<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (error) {
      throw ProductApiException(_mapDioError(error));
    }
  }

  ApiError _mapDioError(DioException error) {
    final data = error.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
      traceId: error.response?.headers.value('x-trace-id'),
    );
  }
}
