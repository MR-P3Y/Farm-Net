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
      clearFinalPrice: true,
      clearPaymentAttempt: true,
    );
    try {
      final request = await _repository.requestDetail(id);
      final finalPrice = await _repository.requestFinalPrice(id);
      state = state.copyWith(
        isLoading: false,
        selected: request,
        finalPrice: finalPrice,
      );
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

  Future<bool> decideFinalPrice(int id, String decision) async {
    if (state.isSaving) return false;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final finalPrice = await _repository.decideFinalPrice(id, decision);
      state = state.copyWith(
        isSaving: false,
        finalPrice: finalPrice,
        successMessage:
            decision == 'accept'
                ? 'قیمت نهایی پذیرفته شد.'
                : 'پیشنهاد قیمت رد شد.',
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
        errorMessage: 'ثبت تصمیم قیمت نهایی ناموفق بود.',
      );
    }
    return false;
  }

  Future<BillingPaymentAttempt?> payInvoice({
    required int requestId,
    required int invoiceId,
    required String provider,
  }) async {
    if (state.isSaving) return null;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
      clearPaymentAttempt: true,
    );
    try {
      var attempt = await _repository.checkoutInvoice(
        invoiceId: invoiceId,
        provider: provider,
        idempotencyKey:
            'mobile-service-invoice-$invoiceId-${DateTime.now().microsecondsSinceEpoch}',
      );
      if (provider == 'mock') {
        attempt = await _repository.verifyInvoicePayment(
          attemptId: attempt.id,
          providerToken: 'mobile-approved',
        );
      }
      final finalPrice = await _repository.requestFinalPrice(requestId);
      state = state.copyWith(
        isSaving: false,
        finalPrice: finalPrice,
        paymentAttempt: attempt,
        successMessage:
            attempt.isSucceeded
                ? 'پرداخت با موفقیت تأیید شد.'
                : 'پرداخت ایجاد شد؛ آن را در درگاه تکمیل کنید.',
      );
      return attempt;
    } on ServiceApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'شروع یا تأیید پرداخت ناموفق بود.',
      );
    }
    return null;
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

  Future<bool> requestRefund(int id, {required String reason}) async {
    if (state.isSaving) return false;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      await _repository.requestRefund(
        requestId: id,
        reason: reason,
        idempotencyKey:
            'mobile-service-refund-$id-${DateTime.now().microsecondsSinceEpoch}',
      );
      final request = await _repository.requestDetail(id);
      final finalPrice = await _repository.requestFinalPrice(id);
      state = state.copyWith(
        isSaving: false,
        selected: request,
        finalPrice: finalPrice,
        successMessage:
            finalPrice?.refundReviewRequired == true
                ? 'درخواست لغو و بازپرداخت برای بررسی ادمین ثبت شد.'
                : 'بازپرداخت کامل تأیید شد و در انتظار پردازش مالی است.',
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
        errorMessage: 'ثبت درخواست بازپرداخت ناموفق بود.',
      );
    }
    return false;
  }

  Future<bool> confirmCompletion(int id) async {
    if (state.isSaving) return false;
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final request = await _repository.confirmCompletion(id);
      state = state.copyWith(
        isSaving: false,
        selected: request,
        requests:
            state.requests
                .map((item) => item.id == id ? request : item)
                .toList(),
        successMessage: 'انجام خدمت تأیید و سهم خدمات‌دهنده آزاد شد.',
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
        errorMessage: 'تأیید انجام خدمت ناموفق بود.',
      );
    }
    return false;
  }
}
