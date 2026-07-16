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

  Future<ServiceRequest> createRequest(ServiceRequestInput input) async =>
      _request(
        () => _client.dio.post<Map<String, dynamic>>(
          '/services/requests',
          data: input.toJson(),
        ),
      );

  Future<List<ServiceRequest>> myRequests({String? status}) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/requests/me',
        queryParameters: status == null ? null : {'status': status},
      );
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ServiceRequest.fromJson)
          .toList();
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceRequest> requestDetail(int id) => _request(
    () => _client.dio.get<Map<String, dynamic>>('/services/requests/$id'),
  );

  Future<ServiceRequest> cancelRequest(int id, {String? reason}) => _request(
    () => _client.dio.patch<Map<String, dynamic>>(
      '/services/requests/$id/cancel',
      data: {'reason': reason},
    ),
  );

  Future<ServiceRequest> _request(
    Future<Response<Map<String, dynamic>>> Function() call,
  ) async {
    try {
      final response = await call();
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceProviderProfileOwner?> myProviderProfile() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/me/provider-profile',
      );
      final data = response.data?['data'];
      if (data == null || data is Map && data.isEmpty) return null;
      return ServiceProviderProfileOwner.fromJson(data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceProviderProfileOwner> saveProviderProfile(
    ServiceProviderProfileInput input, {
    required bool create,
  }) async {
    try {
      final response =
          create
              ? await _client.dio.post<Map<String, dynamic>>(
                '/services/me/provider-profile',
                data: input.toJson(),
              )
              : await _client.dio.put<Map<String, dynamic>>(
                '/services/me/provider-profile',
                data: input.toJson(),
              );
      return ServiceProviderProfileOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceProviderProfileOwner> submitProviderProfile() async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/services/me/provider-profile/submit',
      );
      return ServiceProviderProfileOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<List<ServiceOfferOwner>> myOffers() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/services/me/offers',
      );
      return (response.data?['data'] as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ServiceOfferOwner.fromJson)
          .toList();
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceOfferOwner> saveOffer(
    ServiceOfferInput input, {
    int? offerId,
  }) async {
    try {
      final response =
          offerId == null
              ? await _client.dio.post<Map<String, dynamic>>(
                '/services/me/offers',
                data: input.toJson(),
              )
              : await _client.dio.put<Map<String, dynamic>>(
                '/services/me/offers/$offerId',
                data: input.toJson(),
              );
      return ServiceOfferOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw ServiceApiException(_mapError(error));
    }
  }

  Future<ServiceOfferOwner> submitOffer(int id) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/services/me/offers/$id/submit',
      );
      return ServiceOfferOwner.fromJson(
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
