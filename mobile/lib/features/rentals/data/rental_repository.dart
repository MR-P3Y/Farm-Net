import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'rental_api.dart';
import 'rental_models.dart';

final rentalRepositoryProvider = Provider<RentalRepository>(
  (ref) => RentalRepository(api: RentalApi()),
);

class RentalRepository {
  RentalRepository({required RentalApi api}) : _api = api;
  final RentalApi _api;

  Future<List<RentalCategory>> categories() => _api.categories();
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
  }) => _api.equipment(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    operatorMode: operatorMode,
    minPrice: minPrice,
    maxPrice: maxPrice,
    availableFrom: availableFrom,
    availableTo: availableTo,
    sort: sort,
  );
  Future<RentalEquipmentDetail> detail(int id) => _api.detail(id);
  Future<RentalAvailabilityCheck> availability(
    int id,
    DateTime start,
    DateTime end,
  ) => _api.availability(id, start, end);
  Future<RentalRequest> createRequest(RentalRequestInput input) =>
      _api.createRequest(input);
  Future<List<RentalRequest>> myRequests({String? status}) =>
      _api.myRequests(status: status);
  Future<RentalRequest> requestDetail(int id) => _api.requestDetail(id);
  Future<RentalRequest> cancelRequest(int id, String reason) =>
      _api.cancelRequest(id, reason);
  Future<LessorProfile?> myProfile() => _api.myProfile();
  Future<LessorProfile> saveProfile(LessorProfileInput input) =>
      _api.saveProfile(input);
  Future<LessorProfile> submitProfile() => _api.submitProfile();
  Future<List<RentalEquipmentOwner>> myEquipment() => _api.myEquipment();
  Future<RentalEquipmentOwner> saveEquipment(
    RentalEquipmentInput input, {
    int? id,
  }) => _api.saveEquipment(input, id: id);
  Future<RentalEquipmentOwner> submitEquipment(int id) =>
      _api.submitEquipment(id);
  Future<List<RentalPricingRule>> ownerPricing(int id) => _api.ownerPricing(id);
  Future<List<RentalPricingRule>> replacePricing(
    int id,
    List<RentalPricingRule> rows,
  ) => _api.replacePricing(id, rows);
  Future<List<RentalAvailabilityBlock>> ownerAvailability(int id) =>
      _api.ownerAvailability(id);
  Future<RentalAvailabilityBlock> createAvailability(
    int id,
    RentalAvailabilityBlock row,
  ) => _api.createAvailability(id, row);
  Future<RentalAvailabilityBlock> updateAvailability(
    int id,
    RentalAvailabilityBlock row,
  ) => _api.updateAvailability(id, row);
  Future<void> deleteAvailability(int equipmentId, int blockId) =>
      _api.deleteAvailability(equipmentId, blockId);
  Future<List<RentalRequest>> assignedRequests({String? status}) =>
      _api.assignedRequests(status: status);
  Future<RentalRequest> assignedDetail(int id) => _api.assignedDetail(id);
  Future<RentalRequest> updateAssigned(int id, String status, {String? note}) =>
      _api.updateAssigned(id, status, note: note);
}
