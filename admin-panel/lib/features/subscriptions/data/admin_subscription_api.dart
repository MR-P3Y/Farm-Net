import 'package:dio/dio.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/network/admin_api_client.dart';
import '../../../core/network/admin_api_error.dart';
import '../../../core/storage/admin_token_storage.dart';
import 'admin_subscription_models.dart';

class AdminSubscriptionApiException implements Exception {
  const AdminSubscriptionApiException(this.error);
  final AdminApiError error;
}

class AdminSubscriptionApi {
  AdminSubscriptionApi({
    AdminApiClient? client,
    AdminTokenStorage? tokenStorage,
  }) : _client = client ?? AdminApiClient(baseUrl: AdminConfig.apiBaseUrl),
       _tokens = tokenStorage ?? AdminTokenStorage();

  final AdminApiClient _client;
  final AdminTokenStorage _tokens;

  Future<AdminBillingPage<AdminBillingPlan>> plans({
    String? query,
    String? status,
    int page = 1,
  }) async {
    final json = await _request(
      'GET',
      '/admin/billing/plans',
      query: {
        if (query?.isNotEmpty == true) 'q': query,
        if (status?.isNotEmpty == true) 'status': status,
        'page': page,
        'page_size': 20,
      },
    );
    return _page(json, (item) => AdminBillingPlan.fromJson(item));
  }

  Future<AdminBillingPlan> createPlan(Map<String, dynamic> payload) async {
    final json = await _request('POST', '/admin/billing/plans', data: payload);
    return AdminBillingPlan.fromJson((json['data'] as Map).cast());
  }

  Future<AdminBillingPlan> setPlanStatus(
    AdminBillingPlan plan,
    String status,
  ) async {
    final json = await _request(
      'PATCH',
      '/admin/billing/plans/${plan.id}/status',
      data: {'expected_version': plan.version, 'status': status},
    );
    return AdminBillingPlan.fromJson((json['data'] as Map).cast());
  }

  Future<AdminBillingPage<AdminBillingSubscription>> subscriptions({
    String? query,
    String? status,
    int page = 1,
  }) async {
    final json = await _request(
      'GET',
      '/admin/billing/subscriptions',
      query: {
        if (query?.isNotEmpty == true) 'q': query,
        if (status?.isNotEmpty == true) 'status': status,
        'page': page,
        'page_size': 20,
      },
    );
    return _page(json, (item) => AdminBillingSubscription.fromJson(item));
  }

  Future<AdminBillingSubscription> subscription(int id) async {
    final json = await _request('GET', '/admin/billing/subscriptions/$id');
    return AdminBillingSubscription.fromJson((json['data'] as Map).cast());
  }

  Future<AdminBillingSubscription> manualActivate({
    required int userId,
    required int planId,
    required String reason,
  }) async {
    final json = await _request(
      'POST',
      '/admin/billing/subscriptions/manual-activate',
      data: {'user_id': userId, 'plan_id': planId, 'reason': reason},
    );
    return AdminBillingSubscription.fromJson((json['data'] as Map).cast());
  }

  Future<AdminBillingSubscription> cancel({
    required AdminBillingSubscription subscription,
    required String reason,
    required bool atPeriodEnd,
  }) async {
    final json = await _request(
      'PATCH',
      '/admin/billing/subscriptions/${subscription.id}/cancel',
      data: {
        'expected_version': subscription.version,
        'reason': reason,
        'cancel_at_period_end': atPeriodEnd,
      },
    );
    return AdminBillingSubscription.fromJson((json['data'] as Map).cast());
  }

  Future<AdminBillingPage<AdminBillingAudit>> audit({
    String? action,
    String? targetType,
    int page = 1,
  }) async {
    final json = await _request(
      'GET',
      '/admin/billing/audit',
      query: {
        if (action?.isNotEmpty == true) 'action': action,
        if (targetType?.isNotEmpty == true) 'target_type': targetType,
        'page': page,
        'page_size': 20,
      },
    );
    return _page(json, AdminBillingAudit.fromJson);
  }

  Future<AdminBillingReconciliation> reconciliation() async {
    final json = await _request('GET', '/admin/billing/reconciliation');
    return AdminBillingReconciliation.fromJson(
      (json['data'] as Map).cast<String, dynamic>(),
    );
  }

  Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, dynamic>? query,
    Map<String, dynamic>? data,
  }) async {
    _client.setToken(await _tokens.getAccessToken());
    try {
      final response = await _client.dio.request<Map<String, dynamic>>(
        path,
        data: data,
        queryParameters: query,
        options: Options(method: method),
      );
      return response.data ?? <String, dynamic>{};
    } on DioException catch (error) {
      final body = error.response?.data;
      throw AdminSubscriptionApiException(
        body is Map<String, dynamic>
            ? AdminApiError.fromJson(body)
            : AdminApiError(
              code: 'NETWORK_ERROR',
              message: error.message ?? 'Network error',
            ),
      );
    }
  }

  AdminBillingPage<T> _page<T>(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) parser,
  ) {
    final meta = (json['meta'] as Map).cast<String, dynamic>();
    return AdminBillingPage<T>(
      items:
          (json['data'] as List)
              .map((item) => parser((item as Map).cast<String, dynamic>()))
              .toList(),
      page: (meta['page'] as num).toInt(),
      total: (meta['total'] as num).toInt(),
      totalPages: (meta['total_pages'] as num).toInt(),
    );
  }
}
