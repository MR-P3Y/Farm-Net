import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'rental_models.dart';

class RentalApiException implements Exception {
  const RentalApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class RentalApi {
  RentalApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<List<RentalEquipment>> equipment({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? operatorMode,
    num? minPrice,
    num? maxPrice,
    DateTime? availableFrom,
    DateTime? availableTo,
    String? sort,
  }) => listPublic(
    q: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    operatorMode: operatorMode,
    availableFrom: availableFrom,
    availableTo: availableTo,
  );

  Future<List<RentalEquipment>> listPublic({
    String? q,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? operatorMode,
    DateTime? availableFrom,
    DateTime? availableTo,
  }) async {
    final params = <String, dynamic>{};
    if (q != null && q.isNotEmpty) params['q'] = q;
    if (categoryId != null) params['category_id'] = categoryId;
    if (provinceId != null) params['province_id'] = provinceId;
    if (cityId != null) params['city_id'] = cityId;
    if (operatorMode != null) params['operator_mode'] = operatorMode;

    try {
      final response = await _client.get(
        'rentals/discovery',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => RentalEquipment.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalEquipmentDetail> detail(int id) async {
    try {
      final response = await _client.get('rentals/discovery/$id');
      final data = response.data?['data'] as Map<String, dynamic>;
      return RentalEquipmentDetail(
        equipment: RentalEquipment.fromJson(data),
        pricing:
            (data['pricing_rules'] as List? ?? [])
                .whereType<Map<String, dynamic>>()
                .map(RentalPricingRule.fromJson)
                .toList(),
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalCategory>> categories() async {
    try {
      final response = await _client.get('rentals/categories');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => RentalCategory.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalRequest> createRequest(RentalRequestInput input) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/requests',
        data: input.toJson(),
      );
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalRequest>> myRequests({String? status}) async {
    await _auth();
    final params = <String, dynamic>{};
    if (status != null) params['status'] = status;
    try {
      final response = await _client.get(
        'rentals/requests/me',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => RentalRequest.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalRequest> requestDetail(int id) async {
    await _auth();
    try {
      final response = await _client.get('rentals/requests/$id');
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalRequest> cancelRequest(int id, String reason) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/requests/$id/cancel',
        data: {'cancel_reason': reason},
      );
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<bool> checkAvailability(
    int equipmentId,
    DateTime startsAt,
    DateTime endsAt,
  ) async {
    try {
      final response = await _client.get(
        'rentals/discovery/$equipmentId/check',
        queryParameters: {
          'starts_at': startsAt.toIso8601String(),
          'ends_at': endsAt.toIso8601String(),
        },
      );
      return response.data?['data']?['available'] == true;
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalAvailabilityCheck> availability(
    int equipmentId,
    DateTime startsAt,
    DateTime endsAt,
  ) async => RentalAvailabilityCheck(
    isAvailable: await checkAvailability(equipmentId, startsAt, endsAt),
  );

  // Management (Lessor)
  Future<LessorProfile?> myProfile() async {
    await _auth();
    try {
      final response = await _client.get('rentals/management/profile');
      final data = response.data?['data'];
      return data == null
          ? null
          : LessorProfile.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      throw RentalApiException(_error(e));
    }
  }

  Future<LessorProfile> saveProfile(LessorProfileInput input) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/profile',
        data: input.toJson(),
      );
      return LessorProfile.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<LessorProfile> submitProfile() async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/profile/submit',
        data: {},
      );
      return LessorProfile.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalEquipmentOwner>> myEquipment() async {
    await _auth();
    try {
      final response = await _client.get('rentals/management/equipment');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map(
            (item) =>
                RentalEquipmentOwner.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalEquipmentOwner> saveEquipment(
    RentalEquipmentInput input, {
    required int? id,
  }) async {
    await _auth();
    try {
      final response =
          id == null
              ? await _client.post(
                'rentals/management/equipment',
                data: input.toJson(),
              )
              : await _client.put(
                'rentals/management/equipment/$id',
                data: input.toJson(),
              );
      return RentalEquipmentOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalEquipmentOwner> submitEquipment(int id) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/equipment/$id/submit',
        data: {},
      );
      return RentalEquipmentOwner.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalPricingRule>> ownerPricing(int id) async {
    await _auth();
    try {
      final response = await _client.get(
        'rentals/management/equipment/$id/pricing',
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map(
            (item) => RentalPricingRule.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalPricingRule>> replacePricing(
    int id,
    List<RentalPricingRule> rules,
  ) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/equipment/$id/pricing',
        data: {'rules': rules.map((r) => r.toInputJson()).toList()},
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map(
            (item) => RentalPricingRule.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalAvailabilityBlock>> ownerAvailability(int id) async {
    await _auth();
    try {
      final response = await _client.get(
        'rentals/management/equipment/$id/availability',
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map(
            (item) =>
                RentalAvailabilityBlock.fromJson(item as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalAvailabilityBlock> createAvailability(
    int id,
    RentalAvailabilityBlock block,
  ) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/equipment/$id/availability',
        data: block.toJson(),
      );
      return RentalAvailabilityBlock.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalAvailabilityBlock> updateAvailability(
    int equipmentId,
    RentalAvailabilityBlock block,
  ) async {
    await _auth();
    try {
      final response = await _client.patch(
        'rentals/management/equipment/$equipmentId/availability/${block.id}',
        data: block.toJson(),
      );
      return RentalAvailabilityBlock.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<void> deleteAvailability(int equipmentId, int blockId) async {
    await _auth();
    try {
      await _client.delete(
        'rentals/management/equipment/$equipmentId/availability/$blockId',
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<List<RentalRequest>> assignedRequests({String? status}) async {
    await _auth();
    final params = <String, dynamic>{};
    if (status != null) params['status'] = status;
    try {
      final response = await _client.get(
        'rentals/management/requests',
        queryParameters: params,
      );
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => RentalRequest.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalRequest> assignedDetail(int id) async {
    await _auth();
    try {
      final response = await _client.get('rentals/management/requests/$id');
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
    }
  }

  Future<RentalRequest> updateAssigned(
    int requestId,
    String status, {
    String? note,
  }) async {
    await _auth();
    try {
      final response = await _client.post(
        'rentals/management/requests/$requestId/transition',
        data: {'to_status': status, 'note': note},
      );
      return RentalRequest.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw RentalApiException(_error(e));
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
      message: error.message ?? 'خطا در عملیات اجاره',
    );
  }
}
