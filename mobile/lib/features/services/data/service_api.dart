import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'service_models.dart';

class ServiceApiException implements Exception {
  const ServiceApiException(this.error);
  final ApiError error;
}

class ServiceApi {
  ServiceApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final ApiClient _client;

  Future<List<ServiceCategory>> categories() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/categories',
      );
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ServiceCategory.fromJson)
          .toList();
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<List<ServiceOffer>> offers({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
  }) async {
    final params = <String, dynamic>{};
    if (query?.trim().isNotEmpty ?? false) params['q'] = query!.trim();
    if (categoryId != null) params['category_id'] = categoryId;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (pricingType?.isNotEmpty ?? false) params['pricing_type'] = pricingType;
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/offers',
        queryParameters: params,
      );
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ServiceOffer.fromJson)
          .toList();
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceOffer> detail(int id) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/offers/$id',
      );
      return ServiceOffer.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  ApiError _mapError(DioException error) {
    final data = error.response?.data;
    return data is Map<String, dynamic>
        ? ApiError.fromJson(data)
        : ApiError(
          code: 'NETWORK_ERROR',
          message: error.message ?? 'Network error',
        );
  }
}
