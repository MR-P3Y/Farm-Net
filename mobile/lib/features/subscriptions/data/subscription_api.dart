import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/network/api_error_mapper.dart';
import 'subscription_models.dart';

class SubscriptionApiException implements Exception {
  const SubscriptionApiException(this.error);
  final ApiError error;
}

class SubscriptionApi {
  SubscriptionApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<SubscriptionPlan>> plans() => _request(() async {
    final response = await _client.get('/billing/plans');
    return _list(response.data?['data'], SubscriptionPlan.fromJson);
  });

  Future<OwnSubscription?> current() => _request(() async {
    final response = await _client.get('/billing/subscription/me');
    final data = response.data?['data'];
    return data is Map
        ? OwnSubscription.fromJson(data.cast<String, dynamic>())
        : null;
  });

  Future<List<SubscriptionEntitlement>> entitlements() => _request(() async {
    final response = await _client.get('/billing/entitlements/me');
    return _list(response.data?['data'], SubscriptionEntitlement.fromJson);
  });

  Future<List<SubscriptionUsage>> usage() => _request(() async {
    final response = await _client.get('/billing/usage/me');
    return _list(response.data?['data'], SubscriptionUsage.fromJson);
  });

  Future<OwnSubscription> activateFree() => _request(() async {
    final response = await _client.post('/billing/subscription/free');
    return OwnSubscription.fromJson(
      (response.data!['data'] as Map).cast<String, dynamic>(),
    );
  });

  Future<SubscriptionCheckout> checkout({
    required String planCode,
    required String provider,
    required String idempotencyKey,
  }) => _request(() async {
    final response = await _client.post(
      '/billing/checkout',
      data: {
        'plan_code': planCode,
        'provider': provider,
        'idempotency_key': idempotencyKey,
      },
    );
    return SubscriptionCheckout.fromJson(
      (response.data!['data'] as Map).cast<String, dynamic>(),
    );
  });

  Future<SubscriptionCheckout> renewalCheckout({
    required String provider,
    required String idempotencyKey,
  }) => _request(() async {
    final response = await _client.post(
      '/billing/subscription/renew/checkout',
      data: {'provider': provider, 'idempotency_key': idempotencyKey},
    );
    return SubscriptionCheckout.fromJson(
      (response.data!['data'] as Map).cast<String, dynamic>(),
    );
  });

  Future<SubscriptionCheckout> verify({
    required int paymentAttemptId,
    required String providerToken,
  }) => _request(() async {
    final response = await _client.post(
      '/billing/payments/verify',
      data: {
        'payment_attempt_id': paymentAttemptId,
        'provider_token': providerToken,
      },
    );
    return SubscriptionCheckout.fromJson(
      (response.data!['data'] as Map).cast<String, dynamic>(),
    );
  });

  Future<OwnSubscription> cancel({
    required int expectedVersion,
    required String reason,
  }) => _request(() async {
    final response = await _client.post(
      '/billing/subscription/cancel',
      data: {
        'expected_version': expectedVersion,
        'cancel_at_period_end': true,
        'reason': reason,
      },
    );
    return OwnSubscription.fromJson(
      (response.data!['data'] as Map).cast<String, dynamic>(),
    );
  });

  Future<OwnSubscription> resume({required int expectedVersion}) =>
      _request(() async {
        final response = await _client.post(
          '/billing/subscription/resume',
          data: {'expected_version': expectedVersion},
        );
        return OwnSubscription.fromJson(
          (response.data!['data'] as Map).cast<String, dynamic>(),
        );
      });

  Future<T> _request<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw SubscriptionApiException(mapApiError(error));
    }
  }

  List<T> _list<T>(dynamic data, T Function(Map<String, dynamic>) parser) =>
      (data as List? ?? const [])
          .map((row) => parser((row as Map).cast<String, dynamic>()))
          .toList();
}
