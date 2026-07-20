import 'package:dio/dio.dart';

import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import 'consultant_models.dart';

class ConsultantApiException implements Exception {
  const ConsultantApiException(this.error);

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}

class ConsultantApi {
  ConsultantApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);

  final ApiClient _client;

  Future<List<ConsultantSpecialtyModel>> specialties() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/specialties',
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultantSpecialtyModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<List<ConsultantProfileModel>> list({
    int? specialtyId,
    String? query,
    int? provinceId,
    int? cityId,
    String? sort,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final params = <String, dynamic>{'page': page, 'page_size': pageSize};

      if (specialtyId != null) params['specialty_id'] = specialtyId;
      if (provinceId != null) params['province_id'] = provinceId;
      if (cityId != null) params['city_id'] = cityId;
      if (sort?.isNotEmpty ?? false) params['sort'] = sort;
      if (query != null && query.trim().isNotEmpty) {
        params['q'] = query.trim();
      }

      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultantProfileModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel> detail(int profileId) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/$profileId',
      );
      final json = response.data ?? {};

      return ConsultantProfileModel.fromJson(
        json['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel?> myProfile() async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/me/profile',
      );
      final data = response.data?['data'];

      if (data == null) return null;

      return ConsultantProfileModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel> saveMyProfile({
    required ConsultantProfileInput input,
    required bool create,
  }) async {
    try {
      final response =
          create
              ? await _client.dio.post<Map<String, dynamic>>(
                '/consultants/me/profile',
                data: input.toJson(),
              )
              : await _client.dio.put<Map<String, dynamic>>(
                '/consultants/me/profile',
                data: input.toJson(),
              );

      return ConsultantProfileModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel> submitMyProfile() async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/consultants/me/profile/submit',
      );

      return ConsultantProfileModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultationRequestModel> createRequest({
    required int? consultantProfileId,
    required int? specialtyId,
    required String title,
    required String description,
    required String contactMethod,
  }) async {
    try {
      final response = await _client.dio.post<Map<String, dynamic>>(
        '/consultants/requests',
        data: {
          'consultant_profile_id': consultantProfileId,
          'specialty_id': specialtyId,
          'title': title,
          'description': description,
          'contact_method': contactMethod,
          'currency': 'TOMAN',
        },
      );

      return ConsultationRequestModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<List<ConsultationRequestModel>> myRequests({
    String? status,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final params = <String, dynamic>{'page': page, 'page_size': pageSize};
      if (status != null && status.isNotEmpty) params['status'] = status;

      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/requests/me',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultationRequestModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultationRequestModel> requestDetail(int requestId) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/requests/$requestId',
      );

      return ConsultationRequestModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultationRequestModel> cancelRequest({
    required int requestId,
    String? note,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        '/consultants/requests/$requestId/cancel',
        data: {
          'status': 'cancelled',
          'note': note ?? 'لغو توسط کاربر از اپلیکیشن موبایل',
        },
      );

      return ConsultationRequestModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<List<ConsultationRequestModel>> assignedRequests({
    String? status,
    int page = 1,
    int pageSize = 50,
  }) async {
    try {
      final params = <String, dynamic>{'page': page, 'page_size': pageSize};
      if (status != null && status.isNotEmpty) params['status'] = status;

      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/requests/assigned',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? const [];

      return rows
          .whereType<Map<String, dynamic>>()
          .map(ConsultationRequestModel.fromJson)
          .toList();
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultationRequestModel> assignedRequestDetail(int requestId) async {
    try {
      final response = await _client.dio.get<Map<String, dynamic>>(
        '/consultants/requests/assigned/$requestId',
      );

      return ConsultationRequestModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultationRequestModel> updateAssignedRequestStatus({
    required int requestId,
    required String status,
    String? note,
  }) async {
    try {
      final response = await _client.dio.patch<Map<String, dynamic>>(
        '/consultants/requests/$requestId/status',
        data: {
          'status': status,
          'note': note ?? 'به‌روزرسانی توسط مشاور از اپلیکیشن موبایل',
        },
      );

      return ConsultationRequestModel.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ConsultantApiException(_mapDioError(e));
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
