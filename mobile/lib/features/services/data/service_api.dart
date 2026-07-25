import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'service_models.dart';

class ServiceApiException implements Exception {
  const ServiceApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class ServiceApi {
  ServiceApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<List<ServiceOffer>> offers({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
    num? minPrice,
    num? maxPrice,
    String? sort,
  }) => listPublic(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    pricingType: pricingType,
  );

  Future<List<ServiceOffer>> listPublic({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
  }) async {
    final params = <String, dynamic>{};
    if (query != null && query.isNotEmpty) params['q'] = query;
    if (categoryId != null) params['category_id'] = categoryId;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (pricingType != null) params['pricing_type'] = pricingType;

    try {
      final response = await _client.get(
        'services/discovery',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => ServiceOffer.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceOfferDetail> detail(int id) async {
    try {
      final response = await _client.get('services/discovery/$id');
      return ServiceOfferDetail.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<List<ServiceCategory>> categories() async {
    try {
      final response = await _client.get('services/categories');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => ServiceCategory.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceRequest> createRequest(ServiceRequestInput input) async {
    await _auth();
    try {
      final response = await _client.post(
        'services/requests',
        data: input.toJson(),
      );
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<List<ServiceRequest>> listMyRequests({String? status}) async {
    await _auth();
    final params = <String, dynamic>{};
    if (status != null) params['status'] = status;
    try {
      final response = await _client.get(
        'services/requests/me',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => ServiceRequest.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<List<ServiceRequest>> myRequests({String? status}) =>
      listMyRequests(status: status);

  Future<ServiceRequest> requestDetail(int id) async {
    await _auth();
    try {
      final response = await _client.get('services/requests/$id');
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceRequest> cancelRequest(int id, {required String reason}) async {
    await _auth();
    try {
      final response = await _client.post(
        'services/requests/$id/cancel',
        data: {'cancel_reason': reason},
      );
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  // Management
  Future<ServiceProviderProfileOwner?> myProviderProfile() async {
    await _auth();
    try {
      final response = await _client.get('services/management/profile');
      final data = response.data?['data'];
      return data == null
          ? null
          : ServiceProviderProfileOwner.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceProviderProfileOwner> saveProviderProfile(
    ServiceProviderProfileInput input, {
    required bool create,
  }) async {
    await _auth();
    try {
      final response =
          create
              ? await _client.post(
                'services/management/profile',
                data: input.toJson(),
              )
              : await _client.patch(
                'services/management/profile',
                data: input.toJson(),
              );
      return ServiceProviderProfileOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceProviderProfileOwner> submitProviderProfile() async {
    await _auth();
    try {
      final response = await _client.post(
        'services/management/profile/submit',
        data: {},
      );
      return ServiceProviderProfileOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<List<ServiceOfferOwner>> myOffers() async {
    await _auth();
    try {
      final response = await _client.get('services/management/offers');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map(
            (item) => ServiceOfferOwner.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceOfferOwner> saveOffer(
    ServiceOfferInput input, {
    required int? offerId,
  }) async {
    await _auth();
    try {
      final response =
          offerId == null
              ? await _client.post(
                'services/management/offers',
                data: input.toJson(),
              )
              : await _client.put(
                'services/management/offers/$offerId',
                data: input.toJson(),
              );
      return ServiceOfferOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceOfferOwner> submitOffer(int id) async {
    await _auth();
    try {
      final response = await _client.post(
        'services/management/offers/$id/submit',
        data: {},
      );
      return ServiceOfferOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<List<ServiceRequest>> assignedRequests({
    String? status,
    int? offerId,
    int? categoryId,
  }) async {
    await _auth();
    final params = <String, dynamic>{};
    if (status != null) params['status'] = status;
    if (offerId != null) params['offer_id'] = offerId;
    if (categoryId != null) params['category_id'] = categoryId;
    try {
      final response = await _client.get(
        'services/management/requests',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => ServiceRequest.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceRequest> assignedRequestDetail(int id) async {
    await _auth();
    try {
      final response = await _client.get('services/management/requests/$id');
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<ServiceRequest> updateAssignedRequest(
    int id,
    ServiceRequestStatusUpdateInput input,
  ) async {
    await _auth();
    try {
      final response = await _client.post(
        'services/management/requests/$id/transition',
        data: input.toJson(),
      );
      return ServiceRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw ServiceApiException(_error(e));
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) return ApiError.fromJson(data);
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'خطا در عملیات خدمات',
    );
  }
}
