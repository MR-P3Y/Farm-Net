import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/rental_api.dart';
import '../data/rental_models.dart';
import '../data/rental_repository.dart';

class RentalRequestState {
  const RentalRequestState({
    this.isLoading = false,
    this.isSaving = false,
    this.requests = const [],
    this.selected,
    this.errorMessage,
    this.successMessage,
  });
  final bool isLoading;
  final bool isSaving;
  final List<RentalRequest> requests;
  final RentalRequest? selected;
  final String? errorMessage;
  final String? successMessage;
  RentalRequestState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<RentalRequest>? requests,
    RentalRequest? selected,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) => RentalRequestState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    requests: requests ?? this.requests,
    selected: selected ?? this.selected,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}

final rentalRequestControllerProvider =
    StateNotifierProvider<RentalRequestController, RentalRequestState>(
      (ref) => RentalRequestController(ref.watch(rentalRepositoryProvider)),
    );

class RentalRequestController extends StateNotifier<RentalRequestState> {
  RentalRequestController(this._repository) : super(const RentalRequestState());
  final RentalRepository _repository;

  Future<bool> checkAvailability(int id, DateTime start, DateTime end) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final result = await _repository.availability(id, start, end);
      state = state.copyWith(
        isSaving: false,
        successMessage:
            result.isAvailable ? 'بازه انتخابی در دسترس است.' : null,
        errorMessage:
            result.isAvailable ? null : 'تجهیز در بازه انتخابی در دسترس نیست.',
      );
      return result.isAvailable;
    } on RentalApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'بررسی دسترس‌پذیری ناموفق بود.',
      );
      return false;
    }
  }

  Future<RentalRequest?> create(RentalRequestInput input) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final row = await _repository.createRequest(input);
      state = state.copyWith(
        isSaving: false,
        selected: row,
        successMessage: 'درخواست اجاره ثبت شد.',
      );
      return row;
    } on RentalApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ثبت درخواست اجاره ناموفق بود.',
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
      state = state.copyWith(
        isLoading: false,
        requests: await _repository.myRequests(status: status),
      );
    } on RentalApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
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
      state = state.copyWith(
        isLoading: false,
        selected: await _repository.requestDetail(id),
      );
    } on RentalApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت جزئیات درخواست ناموفق بود.',
      );
    }
  }

  Future<bool> cancel(int id, String reason) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final row = await _repository.cancelRequest(id, reason);
      state = state.copyWith(
        isSaving: false,
        selected: row,
        requests:
            state.requests.map((item) => item.id == id ? row : item).toList(),
        successMessage: 'درخواست اجاره لغو شد.',
      );
      return true;
    } on RentalApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'لغو درخواست ناموفق بود.',
      );
    }
    return false;
  }
}
