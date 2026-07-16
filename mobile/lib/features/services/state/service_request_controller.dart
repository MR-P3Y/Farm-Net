import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/service_api.dart';
import '../data/service_models.dart';
import '../data/service_repository.dart';
import 'service_request_state.dart';

final serviceRequestControllerProvider =
    StateNotifierProvider<ServiceRequestController, ServiceRequestState>(
      (ref) => ServiceRequestController(
        repository: ref.watch(serviceRepositoryProvider),
      ),
    );

class ServiceRequestController extends StateNotifier<ServiceRequestState> {
  ServiceRequestController({required ServiceRepository repository})
    : _repository = repository,
      super(const ServiceRequestState());
  final ServiceRepository _repository;

  Future<ServiceRequest?> create(ServiceRequestInput input) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final request = await _repository.createRequest(input);
      state = state.copyWith(
        isSaving: false,
        selected: request,
        successMessage: 'درخواست خدمت ثبت شد.',
      );
      return request;
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ثبت درخواست خدمت ناموفق بود.',
      );
    }
    return null;
  }

  Future<void> loadList({String? status}) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final requests = await _repository.myRequests(status: status);
      state = state.copyWith(isLoading: false, requests: requests);
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت درخواست‌ها ناموفق بود.',
      );
    }
  }

  Future<void> loadDetail(int id) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final request = await _repository.requestDetail(id);
      state = state.copyWith(isLoading: false, selected: request);
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت جزئیات درخواست ناموفق بود.',
      );
    }
  }

  Future<bool> cancel(int id, {String? reason}) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final request = await _repository.cancelRequest(id, reason: reason);
      state = state.copyWith(
        isSaving: false,
        selected: request,
        requests:
            state.requests
                .map((item) => item.id == id ? request : item)
                .toList(),
        successMessage: 'درخواست خدمت لغو شد.',
      );
      return true;
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'لغو درخواست ناموفق بود.',
      );
    }
    return false;
  }
}
