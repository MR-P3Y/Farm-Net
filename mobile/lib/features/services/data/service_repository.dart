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
    double? latitude,
    double? longitude,
    double? radiusKm,
  }) => _api.offers(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    pricingType: pricingType,
    minPrice: minPrice,
    maxPrice: maxPrice,
    sort: sort,
    latitude: latitude,
    longitude: longitude,
    radiusKm: radiusKm,
  );
  Future<ServiceOffer> detail(int id) async => (await _api.detail(id)).offer;
  Future<ServiceRequest> createRequest(ServiceRequestInput input) =>
      _api.createRequest(input);
  Future<List<ServiceRequest>> myRequests({String? status}) =>
      _api.myRequests(status: status);
  Future<ServiceRequest> requestDetail(int id) => _api.requestDetail(id);
  Future<ServiceRequest> cancelRequest(int id, {String? reason}) =>
      _api.cancelRequest(id, reason: reason ?? '');
  Future<ServiceBillingRefund> requestRefund({
    required int requestId,
    required String reason,
    required String idempotencyKey,
  }) => _api.requestRefund(
    requestId: requestId,
    reason: reason,
    idempotencyKey: idempotencyKey,
  );
  Future<ServiceRequest> confirmCompletion(int requestId) =>
      _api.confirmCompletion(requestId);
  Future<ServiceFinalPrice?> requestFinalPrice(int id) =>
      _api.requestFinalPrice(id);
  Future<ServiceFinalPrice> decideFinalPrice(int id, String decision) =>
      _api.decideFinalPrice(id, decision);
  Future<BillingPaymentAttempt> checkoutInvoice({
    required int invoiceId,
    required String provider,
    required String idempotencyKey,
  }) => _api.checkoutInvoice(
    invoiceId: invoiceId,
    provider: provider,
    idempotencyKey: idempotencyKey,
  );
  Future<BillingPaymentAttempt> verifyInvoicePayment({
    required int attemptId,
    required String providerToken,
  }) => _api.verifyInvoicePayment(
    attemptId: attemptId,
    providerToken: providerToken,
  );
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
  Future<ServiceFinalPrice?> assignedRequestFinalPrice(int id) =>
      _api.assignedRequestFinalPrice(id);
  Future<ServiceFinalPrice> proposeFinalPrice({
    required int requestId,
    required double amount,
    required String description,
  }) => _api.proposeFinalPrice(
    requestId: requestId,
    amount: amount,
    description: description,
  );
  Future<ServiceRequest> updateAssignedRequest(
    int id,
    ServiceRequestStatusUpdateInput input,
  ) => _api.updateAssignedRequest(id, input);
}
