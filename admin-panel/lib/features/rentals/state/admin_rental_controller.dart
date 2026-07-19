import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/admin_rental_api.dart';
import '../data/admin_rental_models.dart';

final adminRentalControllerProvider =
    StateNotifierProvider<AdminRentalController, AdminRentalState>(
      (ref) => AdminRentalController(AdminRentalApi()),
    );

class AdminRentalState {
  const AdminRentalState({
    this.loading = true,
    this.saving = false,
    this.categories = const [],
    this.profiles = const [],
    this.equipment = const [],
    this.requests = const [],
    this.profilePage = 1,
    this.profileTotal = 0,
    this.equipmentPage = 1,
    this.equipmentTotal = 0,
    this.requestPage = 1,
    this.requestTotal = 0,
    this.error,
  });
  final bool loading, saving;
  final List<AdminRentalCategory> categories;
  final List<AdminLessorProfile> profiles;
  final List<AdminRentalEquipment> equipment;
  final List<AdminRentalRequest> requests;
  final int profilePage,
      profileTotal,
      equipmentPage,
      equipmentTotal,
      requestPage,
      requestTotal;
  final String? error;
  AdminRentalState copyWith({
    bool? loading,
    bool? saving,
    List<AdminRentalCategory>? categories,
    List<AdminLessorProfile>? profiles,
    List<AdminRentalEquipment>? equipment,
    List<AdminRentalRequest>? requests,
    int? profilePage,
    int? profileTotal,
    int? equipmentPage,
    int? equipmentTotal,
    int? requestPage,
    int? requestTotal,
    String? error,
    bool clearError = false,
  }) => AdminRentalState(
    loading: loading ?? this.loading,
    saving: saving ?? this.saving,
    categories: categories ?? this.categories,
    profiles: profiles ?? this.profiles,
    equipment: equipment ?? this.equipment,
    requests: requests ?? this.requests,
    profilePage: profilePage ?? this.profilePage,
    profileTotal: profileTotal ?? this.profileTotal,
    equipmentPage: equipmentPage ?? this.equipmentPage,
    equipmentTotal: equipmentTotal ?? this.equipmentTotal,
    requestPage: requestPage ?? this.requestPage,
    requestTotal: requestTotal ?? this.requestTotal,
    error: clearError ? null : error ?? this.error,
  );
}

class AdminRentalController extends StateNotifier<AdminRentalState> {
  AdminRentalController(this.api) : super(const AdminRentalState());
  final AdminRentalApi api;
  Future<void> load() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final r = await Future.wait([
        api.categories(),
        api.profiles(),
        api.equipment(),
        api.requests(),
      ]);
      final p = r[1] as AdminRentalPage<AdminLessorProfile>,
          e = r[2] as AdminRentalPage<AdminRentalEquipment>,
          q = r[3] as AdminRentalPage<AdminRentalRequest>;
      state = state.copyWith(
        loading: false,
        categories: r[0] as List<AdminRentalCategory>,
        profiles: p.items,
        profilePage: p.page,
        profileTotal: p.total,
        equipment: e.items,
        equipmentPage: e.page,
        equipmentTotal: e.total,
        requests: q.items,
        requestPage: q.page,
        requestTotal: q.total,
      );
    } catch (e) {
      _fail(e, loading: false);
    }
  }

  Future<void> page(String kind, int page) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      if (kind == 'profile') {
        final r = await api.profiles(page: page);
        state = state.copyWith(
          saving: false,
          profiles: r.items,
          profilePage: r.page,
          profileTotal: r.total,
        );
      } else if (kind == 'equipment') {
        final r = await api.equipment(page: page);
        state = state.copyWith(
          saving: false,
          equipment: r.items,
          equipmentPage: r.page,
          equipmentTotal: r.total,
        );
      } else {
        final r = await api.requests(page: page);
        state = state.copyWith(
          saving: false,
          requests: r.items,
          requestPage: r.page,
          requestTotal: r.total,
        );
      }
    } catch (e) {
      _fail(e);
    }
  }

  Future<bool> saveCategory(int? id, Map<String, dynamic> data) =>
      _action(() async {
        await api.saveCategory(id, data);
        state = state.copyWith(categories: await api.categories());
      });
  Future<bool> moderate(String kind, int id, String status, String? note) =>
      _action(() async {
        if (kind == 'profile') {
          await api.profileStatus(id, status, note);
          final r = await api.profiles(page: state.profilePage);
          state = state.copyWith(profiles: r.items);
        } else if (kind == 'equipment') {
          await api.equipmentStatus(id, status, note);
          final r = await api.equipment(page: state.equipmentPage);
          state = state.copyWith(equipment: r.items);
        } else {
          await api.requestStatus(id, status, note);
          final r = await api.requests(page: state.requestPage);
          state = state.copyWith(requests: r.items);
        }
      });
  Future<AdminRentalRequest?> detail(int id) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      final r = await api.requestDetail(id);
      state = state.copyWith(saving: false);
      return r;
    } catch (e) {
      _fail(e);
      return null;
    }
  }

  Future<bool> _action(Future<void> Function() fn) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      await fn();
      state = state.copyWith(saving: false);
      return true;
    } catch (e) {
      _fail(e);
      return false;
    }
  }

  void _fail(Object e, {bool? loading}) {
    state = state.copyWith(
      loading: loading,
      saving: false,
      error:
          e is AdminRentalApiException
              ? e.error.message
              : 'خطا در دریافت اطلاعات اجاره تجهیزات',
    );
  }
}
