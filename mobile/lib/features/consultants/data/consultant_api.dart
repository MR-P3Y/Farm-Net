import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'consultant_models.dart';

class ConsultantApiException implements Exception {
  const ConsultantApiException(this.error);
  final ApiError error;
  @override
  String toString() => '${error.code}: ${error.message}';
}

class ConsultantApi {
  ConsultantApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<List<ConsultantProfileModel>> list({
    String? query,
    int? specialtyId,
    int? provinceId,
    int? cityId,
    String? sort,
    int page = 1,
    int pageSize = 20,
  }) async {
    final params = <String, dynamic>{'page': page, 'page_size': pageSize};
    if (query != null && query.isNotEmpty) params['q'] = query;
    if (specialtyId != null) params['specialty_id'] = specialtyId;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (sort != null) params['sort'] = sort;

    final json = await _get('consultants', queryParameters: params);
    final data = json['data'] as List? ?? [];
    return data
        .map((item) => ConsultantProfileModel.fromJson((item as Map).cast()))
        .toList();
  }

  Future<ConsultantProfileModel> detail(int id) async {
    final json = await _get('consultants/$id');
    return ConsultantProfileModel.fromJson((json['data'] as Map).cast());
  }

  Future<List<ConsultantSpecialtyModel>> specialties() async {
    final json = await _get('consultants/specialties');
    final data = json['data'] as List? ?? [];
    return data
        .map((item) => ConsultantSpecialtyModel.fromJson((item as Map).cast()))
        .toList();
  }

  // Management
  Future<ConsultantProfileModel?> myProfile() async {
    await _auth();
    try {
      final json = await _get('consultants/me/profile');
      if (json['data'] == null) return null;
      return ConsultantProfileModel.fromJson((json['data'] as Map).cast());
    } on ConsultantApiException catch (e) {
      if (e.error.code == 'NOT_FOUND') return null;
      rethrow;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      throw ConsultantApiException(_mapDioError(e));
    }
  }

  Future<ConsultantProfileModel> saveMyProfile({
    required ConsultantProfileInput input,
    required bool create,
  }) async {
    await _auth();
    final json =
        create
            ? await _post('consultants/me/profile', data: input.toJson())
            : await _put('consultants/me/profile', data: input.toJson());
    return ConsultantProfileModel.fromJson((json['data'] as Map).cast());
  }

  Future<ConsultantProfileModel> submitMyProfile() async {
    await _auth();
    final json = await _post('consultants/me/profile/submit', data: {});
    return ConsultantProfileModel.fromJson((json['data'] as Map).cast());
  }

  Future<ConsultationRequestModel> createRequest({
    required int? consultantProfileId,
    required int? specialtyId,
    required String title,
    required String description,
    required String contactMethod,
  }) async {
    await _auth();
    final json = await _post(
      'consultants/requests',
      data: {
        'consultant_profile_id': consultantProfileId,
        'specialty_id': specialtyId,
        'title': title,
        'description': description,
        'contact_method': contactMethod,
      },
    );
    return ConsultationRequestModel.fromJson((json['data'] as Map).cast());
  }

  Future<List<ConsultationRequestModel>> myRequests({
    String? status,
    int page = 1,
    int pageSize = 50,
  }) async {
    await _auth();
    final params = <String, dynamic>{'page': page, 'page_size': pageSize};
    if (status != null) params['status'] = status;
    final json = await _get('consultants/requests/me', queryParameters: params);
    final data = json['data'] as List? ?? [];
    return data
        .map((item) => ConsultationRequestModel.fromJson((item as Map).cast()))
        .toList();
  }

  Future<ConsultationRequestModel> requestDetail(int requestId) async {
    await _auth();
    final json = await _get('consultants/requests/$requestId');
    return ConsultationRequestModel.fromJson((json['data'] as Map).cast());
  }

  Future<ConsultationRequestModel> cancelRequest({
    required int requestId,
    String? note,
  }) async {
    await _auth();
    final json = await _patch(
      'consultants/requests/$requestId/cancel',
      data: {'status': 'cancelled', 'note': note},
    );
    return ConsultationRequestModel.fromJson((json['data'] as Map).cast());
  }

  Future<List<ConsultationRequestModel>> assignedRequests({
    String? status,
    int page = 1,
    int pageSize = 50,
  }) async {
    await _auth();
    final params = <String, dynamic>{'page': page, 'page_size': pageSize};
    if (status != null) params['status'] = status;
    final json = await _get(
      'consultants/requests/assigned',
      queryParameters: params,
    );
    final data = json['data'] as List? ?? [];
    return data
        .map((item) => ConsultationRequestModel.fromJson((item as Map).cast()))
        .toList();
  }

  Future<ConsultationRequestModel> assignedRequestDetail(int requestId) async {
    await _auth();
    final json = await _get('consultants/requests/assigned/$requestId');
    return ConsultationRequestModel.fromJson((json['data'] as Map).cast());
  }

  Future<ConsultationRequestModel> updateAssignedRequestStatus({
    required int requestId,
    required String status,
    String? note,
  }) async {
    await _auth();
    final json = await _patch(
      'consultants/requests/$requestId/status',
      data: {'to_status': status, 'note': note},
    );
    return ConsultationRequestModel.fromJson((json['data'] as Map).cast());
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  Future<Map<String, dynamic>> _get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _client.get(
        path,
        queryParameters: queryParameters,
      );
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw ConsultantApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.post(path, data: data);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw ConsultantApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.patch(path, data: data);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw ConsultantApiException(_mapDioError(error));
    }
  }

  Future<Map<String, dynamic>> _put(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      final response = await _client.put(path, data: data);
      return (response.data as Map?)?.cast<String, dynamic>() ?? {};
    } on DioException catch (error) {
      throw ConsultantApiException(_mapDioError(error));
    }
  }

  ApiError _mapDioError(DioException error) {
    final data = error.response?.data;
    if (data is Map) return ApiError.fromJson(data.cast<String, dynamic>());
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
    );
  }
}
