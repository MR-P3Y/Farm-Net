import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_order_models.dart';

class AdminOrderApiException implements Exception {
  const AdminOrderApiException(this.error);

  final AdminApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class AdminOrderApi {
  AdminOrderApi({AdminApiClient? client, AdminTokenStorage? tokenStorage})
    : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokenStorage;

  Future<List<AdminOrder>> listOrders({
    String? status,
    String? paymentStatus,
    int? storeId,
    int? buyerUserId,
  }) async {
    await _setStoredToken();

    final query = <String, String>{'page': '1', 'page_size': '50'};

    if (status != null && status.isNotEmpty) query['status'] = status;
    if (paymentStatus != null && paymentStatus.isNotEmpty) {
      query['payment_status'] = paymentStatus;
    }
    if (storeId != null) query['store_id'] = storeId.toString();
    if (buyerUserId != null) query['buyer_user_id'] = buyerUserId.toString();

    final uri = Uri(path: '/admin/orders', queryParameters: query);
    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => AdminOrder.fromJson((item as Map).cast()))
        .toList();
  }

  Future<AdminOrder> getOrder(int orderId) async {
    await _setStoredToken();

    final json = await _get('/admin/orders/$orderId');
    return AdminOrder.fromJson((json['data'] as Map).cast());
  }

  Future<AdminOrder> updateStatus({
    required int orderId,
    required String status,
    String? adminNote,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/admin/orders/$orderId/status',
      data: {'status': status, 'admin_note': adminNote},
    );

    return AdminOrder.fromJson((json['data'] as Map).cast());
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
      throw AdminOrderApiException(_mapDioError(error));
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
      throw AdminOrderApiException(_mapDioError(error));
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
