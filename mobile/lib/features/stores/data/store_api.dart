import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'store_models.dart';

class StoreApiException implements Exception {
  const StoreApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class StoreApi {
  StoreApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<List<Store>> listPublicStores({
    String? q,
    int? provinceId,
    int? countyId,
    int? cityId,
    String? storeType,
  }) async {
    final query = <String, String>{};

    if (q != null && q.trim().isNotEmpty) query['q'] = q.trim();
    if (provinceId != null) query['province_id'] = provinceId.toString();
    if (countyId != null) query['county_id'] = countyId.toString();
    if (cityId != null) query['city_id'] = cityId.toString();
    if (storeType != null && storeType.trim().isNotEmpty) {
      query['store_type'] = storeType.trim();
    }

    final uri = Uri(
      path: '/public/stores',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Store.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Store> getPublicStoreBySlug(String slug) async {
    final json = await _get('/public/stores/$slug');
    return Store.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Store?> getMyStore() async {
    await _setStoredToken();

    final json = await _get('/stores/me');
    final data = json['data'];

    if (data == null) return null;

    return Store.fromJson(data as Map<String, dynamic>);
  }

  Future<Store> createStore(StoreCreateInput input) async {
    await _setStoredToken();

    final json = await _post('/stores', data: input.toJson());
    return Store.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Store> updateStore({
    required int storeId,
    required StoreUpdateInput input,
  }) async {
    await _setStoredToken();

    final json = await _put('/stores/$storeId', data: input.toJson());
    return Store.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Store> submitStore(int storeId) async {
    await _setStoredToken();

    final json = await _post('/stores/$storeId/submit', data: {});
    return Store.fromJson(json['data'] as Map<String, dynamic>);
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
      throw StoreApiException(_mapDioError(error));
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
      throw StoreApiException(_mapDioError(error));
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
      throw StoreApiException(_mapDioError(error));
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
