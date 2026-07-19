import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'rental_models.dart';

class RentalApiException implements Exception {
  const RentalApiException(this.error);
  final ApiError error;
}

class RentalApi {
  RentalApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final ApiClient _client;

  Future<List<RentalCategory>> categories() async =>
      _getList('/rentals/categories', RentalCategory.fromJson);

  Future<List<RentalEquipment>> equipment({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? operatorMode,
  }) async {
    final params = <String, dynamic>{};
    if (query?.trim().isNotEmpty ?? false) params['q'] = query!.trim();
    if (categoryId != null) params['category_id'] = categoryId;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (operatorMode?.isNotEmpty ?? false) {
      params['operator_mode'] = operatorMode;
    }
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/rentals/equipment',
        queryParameters: params,
      );
      return _parseList(response.data?['data'], RentalEquipment.fromJson);
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  Future<RentalEquipmentDetail> detail(int id) async {
    try {
      final responses = await Future.wait([
        _client.dio.get<Map<String, dynamic>>('/rentals/equipment/$id'),
        _client.dio.get<Map<String, dynamic>>('/rentals/equipment/$id/pricing'),
      ]);
      return RentalEquipmentDetail(
        equipment: RentalEquipment.fromJson(
          responses[0].data?['data'] as Map<String, dynamic>,
        ),
        pricing: _parseList(
          responses[1].data?['data'],
          RentalPricingRule.fromJson,
        ),
      );
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  Future<RentalAvailabilityCheck> availability(
    int equipmentId,
    DateTime startsAt,
    DateTime endsAt,
  ) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/rentals/equipment/$equipmentId/availability',
        queryParameters: {
          'starts_at': startsAt.toUtc().toIso8601String(),
          'ends_at': endsAt.toUtc().toIso8601String(),
        },
      );
      return RentalAvailabilityCheck.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  Future<RentalRequest> createRequest(RentalRequestInput input) => _request(
    () => _client.dio.post<Map<String, dynamic>>(
      '/rentals/requests',
      data: input.toJson(),
    ),
  );
  Future<List<RentalRequest>> myRequests({String? status}) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/rentals/requests/me',
        queryParameters: {if (status != null) 'status': status},
      );
      return _parseList(response.data?['data'], RentalRequest.fromJson);
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  Future<RentalRequest> requestDetail(int id) => _request(
    () => _client.dio.get<Map<String, dynamic>>('/rentals/requests/me/$id'),
  );
  Future<RentalRequest> cancelRequest(int id, String reason) => _request(
    () => _client.dio.post<Map<String, dynamic>>(
      '/rentals/requests/me/$id/cancel',
      data: {'reason': reason},
    ),
  );

  Future<RentalRequest> _request(
    Future<Response<Map<String, dynamic>>> Function() call,
  ) async {
    try {
      final response = await call();
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  Future<List<T>> _getList<T>(
    String path,
    T Function(Map<String, dynamic>) parser,
  ) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(path);
      return _parseList(response.data?['data'], parser);
    } on DioException catch (error) {
      throw RentalApiException(_mapError(error));
    }
  }

  List<T> _parseList<T>(
    Object? data,
    T Function(Map<String, dynamic>) parser,
  ) =>
      (data as List? ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(parser)
          .toList();

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
