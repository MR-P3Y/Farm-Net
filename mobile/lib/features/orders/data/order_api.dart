import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'order_models.dart';

class OrderApiException implements Exception {
  const OrderApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class OrderApi {
  OrderApi({ApiClient? client, TokenStorage? tokenStorage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _tokenStorage;

  Future<Cart> getMyCart() async {
    await _setStoredToken();
    final json = await _get('/cart/me');
    return Cart.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Cart> addCartItem({
    required int productId,
    required int quantity,
  }) async {
    await _setStoredToken();

    final json = await _post(
      '/cart/items',
      data: {'product_id': productId, 'quantity': quantity},
    );

    return Cart.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Cart> updateCartItem({
    required int itemId,
    required int quantity,
  }) async {
    await _setStoredToken();

    final json = await _patch(
      '/cart/items/$itemId',
      data: {'quantity': quantity},
    );

    return Cart.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Cart> deleteCartItem(int itemId) async {
    await _setStoredToken();
    final json = await _delete('/cart/items/$itemId');
    return Cart.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Cart> clearCart() async {
    await _setStoredToken();
    final json = await _delete('/cart/clear');
    return Cart.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<CheckoutResult> checkout(CheckoutInput input) async {
    await _setStoredToken();

    final json = await _post('/checkout', data: input.toJson());

    return CheckoutResult.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<Order>> listMyOrders({String? status}) async {
    await _setStoredToken();

    final query = <String, String>{};
    if (status != null && status.isNotEmpty) query['status'] = status;

    final uri = Uri(
      path: '/orders/me',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Order.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Order> getMyOrder(int orderId) async {
    await _setStoredToken();

    final json = await _get('/orders/$orderId');
    return Order.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<SellerOrderPage> listSellerOrders({
    int page = 1,
    int pageSize = 20,
    String? status,
  }) async {
    await _setStoredToken();
    final query = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };
    if (status != null && status.isNotEmpty) query['status'] = status;
    final uri = Uri(path: '/seller/orders', queryParameters: query);
    return SellerOrderPage.fromEnvelope(await _get(uri.toString()));
  }

  Future<Order> getSellerOrder(int orderId) async {
    await _setStoredToken();
    final json = await _get('/seller/orders/$orderId');
    return Order.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<Order> updateSellerOrderStatus({
    required int orderId,
    required String status,
    String? sellerNote,
  }) async {
    await _setStoredToken();
    final json = await _patch(
      '/seller/orders/$orderId/status',
      data: {
        'status': status,
        if (sellerNote != null && sellerNote.trim().isNotEmpty)
          'seller_note': sellerNote.trim(),
      },
    );
    return Order.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<List<Payment>> listMyPayments({String? status}) async {
    await _setStoredToken();

    final query = <String, String>{};
    if (status != null && status.isNotEmpty) query['status'] = status;

    final uri = Uri(
      path: '/payments/me',
      queryParameters: query.isEmpty ? null : query,
    );

    final json = await _get(uri.toString());
    final data = json['data'] as List? ?? [];

    return data
        .map((item) => Payment.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<PaymentAttempt> initiatePayment({
    required int invoiceId,
    required String idempotencyKey,
  }) async {
    await _setStoredToken();
    final json = await _post(
      '/payments/checkout',
      data: {
        'invoice_id': invoiceId,
        'provider': 'mock',
        'idempotency_key': idempotencyKey,
      },
    );
    return PaymentAttempt.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<PaymentAttempt> verifyPayment({required int attemptId}) async {
    await _setStoredToken();
    final json = await _post(
      '/payments/verify',
      data: {
        'payment_attempt_id': attemptId,
        'provider_payment_id': 'MOCK-$attemptId',
      },
    );
    return PaymentAttempt.fromJson(json['data'] as Map<String, dynamic>);
  }

  Future<void> _setStoredToken() async {
    final token = await _tokenStorage.getAccessToken();
    _client.setToken(token);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw OrderApiException(_mapDioError(e));
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
    } on DioException catch (e) {
      throw OrderApiException(_mapDioError(e));
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
    } on DioException catch (e) {
      throw OrderApiException(_mapDioError(e));
    }
  }

  Future<Map<String, dynamic>> _delete(String path) async {
    try {
      final response = await _client.dio.delete<Map<String, dynamic>>(path);
      return response.data ?? {};
    } on DioException catch (e) {
      throw OrderApiException(_mapDioError(e));
    }
  }

  ApiError _mapDioError(DioException e) {
    final data = e.response?.data;

    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: e.message ?? 'Network error',
      traceId: e.response?.headers.value('x-trace-id'),
    );
  }
}
