import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/rental_api.dart';
import '../data/rental_models.dart';
import '../data/rental_repository.dart';

class RentalManagementState {
  const RentalManagementState({
    this.isLoading = false,
    this.isSaving = false,
    this.profile,
    this.equipment = const [],
    this.categories = const [],
    this.errorMessage,
    this.successMessage,
  });
  final bool isLoading;
  final bool isSaving;
  final LessorProfile? profile;
  final List<RentalEquipmentOwner> equipment;
  final List<RentalCategory> categories;
  final String? errorMessage;
  final String? successMessage;
  RentalManagementState copyWith({
    bool? isLoading,
    bool? isSaving,
    LessorProfile? profile,
    List<RentalEquipmentOwner>? equipment,
    List<RentalCategory>? categories,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) => RentalManagementState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    profile: profile ?? this.profile,
    equipment: equipment ?? this.equipment,
    categories: categories ?? this.categories,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}

final rentalManagementProvider =
    StateNotifierProvider<RentalManagementController, RentalManagementState>(
      (ref) => RentalManagementController(ref.watch(rentalRepositoryProvider)),
    );

class RentalManagementController extends StateNotifier<RentalManagementState> {
  RentalManagementController(this._repo) : super(const RentalManagementState());
  final RentalRepository _repo;
  Future<void> loadProfile() => _load(
    () async =>
        state = state.copyWith(
          isLoading: false,
          profile: await _repo.myProfile(),
        ),
  );
  Future<void> loadEquipment() => _load(() async {
    final values = await Future.wait([_repo.categories(), _repo.myEquipment()]);
    state = state.copyWith(
      isLoading: false,
      categories: values[0] as List<RentalCategory>,
      equipment: values[1] as List<RentalEquipmentOwner>,
    );
  });
  Future<bool> saveProfile(LessorProfileInput input) => _save(
    () async =>
        state = state.copyWith(
          isSaving: false,
          profile: await _repo.saveProfile(input),
          successMessage: 'پروفایل موجر ذخیره شد.',
        ),
  );
  Future<bool> submitProfile() => _save(
    () async =>
        state = state.copyWith(
          isSaving: false,
          profile: await _repo.submitProfile(),
          successMessage: 'پروفایل برای بررسی ارسال شد.',
        ),
  );
  Future<RentalEquipmentOwner?> saveEquipment(
    RentalEquipmentInput input, {
    int? id,
  }) async {
    RentalEquipmentOwner? result;
    final ok = await _save(() async {
      result = await _repo.saveEquipment(input, id: id);
      state = state.copyWith(
        isSaving: false,
        equipment: await _repo.myEquipment(),
        successMessage: 'تجهیز ذخیره شد.',
      );
    });
    return ok ? result : null;
  }

  Future<bool> submitEquipment(int id) => _save(() async {
    await _repo.submitEquipment(id);
    state = state.copyWith(
      isSaving: false,
      equipment: await _repo.myEquipment(),
      successMessage: 'تجهیز برای بررسی ارسال شد.',
    );
  });
  Future<void> _load(Future<void> Function() action) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      await action();
    } on RentalApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت اطلاعات ناموفق بود.',
      );
    }
  }

  Future<bool> _save(Future<void> Function() action) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      await action();
      return true;
    } on RentalApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'ذخیره اطلاعات ناموفق بود.',
      );
      return false;
    }
  }
}

class RentalWorkbenchState {
  const RentalWorkbenchState({
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
  RentalWorkbenchState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<RentalRequest>? requests,
    RentalRequest? selected,
    String? errorMessage,
    String? successMessage,
    bool clearError = false,
    bool clearSuccess = false,
  }) => RentalWorkbenchState(
    isLoading: isLoading ?? this.isLoading,
    isSaving: isSaving ?? this.isSaving,
    requests: requests ?? this.requests,
    selected: selected ?? this.selected,
    errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    successMessage: clearSuccess ? null : successMessage ?? this.successMessage,
  );
}

final rentalWorkbenchProvider =
    StateNotifierProvider<RentalWorkbenchController, RentalWorkbenchState>(
      (ref) => RentalWorkbenchController(ref.watch(rentalRepositoryProvider)),
    );

class RentalWorkbenchController extends StateNotifier<RentalWorkbenchState> {
  RentalWorkbenchController(this._repo) : super(const RentalWorkbenchState());
  final RentalRepository _repo;
  Future<void> loadList({String? status}) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      state = state.copyWith(
        isLoading: false,
        requests: await _repo.assignedRequests(status: status),
      );
    } on RentalApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت میزکار ناموفق بود.',
      );
    }
  }

  Future<void> loadDetail(int id) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      state = state.copyWith(
        isLoading: false,
        selected: await _repo.assignedDetail(id),
      );
    } on RentalApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت درخواست ناموفق بود.',
      );
    }
  }

  Future<bool> update(int id, String status, {String? note}) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSuccess: true,
    );
    try {
      final row = await _repo.updateAssigned(id, status, note: note);
      state = state.copyWith(
        isSaving: false,
        selected: row,
        requests: state.requests.map((e) => e.id == id ? row : e).toList(),
        successMessage: 'وضعیت درخواست به‌روز شد.',
      );
      return true;
    } on RentalApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'به‌روزرسانی وضعیت ناموفق بود.',
      );
      return false;
    }
  }
}
