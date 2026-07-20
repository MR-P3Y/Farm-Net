import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'service_api.dart';
import 'service_models.dart';

final serviceRepositoryProvider = Provider<ServiceRepository>(
  (ref) => ServiceRepository(api: ServiceApi()),
);

class ServiceRepository {
  ServiceRepository({required ServiceApi api}) : _api = api;
  final ServiceApi _api;

  Future<List<ServiceCategory>> categories() => _api.categories();
  Future<List<ServiceOffer>> offers({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? pricingType,
    num? minPrice,
    num? maxPrice,
    String? sort,
  }) => _api.offers(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    pricingType: pricingType,
    minPrice: minPrice,
    maxPrice: maxPrice,
    sort: sort,
  );
  Future<ServiceOffer> detail(int id) => _api.detail(id);
  Future<ServiceRequest> createRequest(ServiceRequestInput input) =>
      _api.createRequest(input);
  Future<List<ServiceRequest>> myRequests({String? status}) =>
      _api.myRequests(status: status);
  Future<ServiceRequest> requestDetail(int id) => _api.requestDetail(id);
  Future<ServiceRequest> cancelRequest(int id, {String? reason}) =>
      _api.cancelRequest(id, reason: reason);
  Future<ServiceProviderProfileOwner?> myProviderProfile() =>
      _api.myProviderProfile();
  Future<ServiceProviderProfileOwner> saveProviderProfile(
    ServiceProviderProfileInput input, {
    required bool create,
  }) => _api.saveProviderProfile(input, create: create);
  Future<ServiceProviderProfileOwner> submitProviderProfile() =>
      _api.submitProviderProfile();
  Future<List<ServiceOfferOwner>> myOffers() => _api.myOffers();
  Future<ServiceOfferOwner> saveOffer(
    ServiceOfferInput input, {
    int? offerId,
  }) => _api.saveOffer(input, offerId: offerId);
  Future<ServiceOfferOwner> submitOffer(int id) => _api.submitOffer(id);
  Future<List<ServiceRequest>> assignedRequests({
    String? status,
    int? offerId,
    int? categoryId,
  }) => _api.assignedRequests(
    status: status,
    offerId: offerId,
    categoryId: categoryId,
  );
  Future<ServiceRequest> assignedRequestDetail(int id) =>
      _api.assignedRequestDetail(id);
  Future<ServiceRequest> updateAssignedRequest(
    int id,
    ServiceRequestStatusUpdateInput input,
  ) => _api.updateAssignedRequest(id, input);
}
