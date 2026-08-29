import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/admin_service_api.dart';
import '../data/admin_service_models.dart';

final adminServiceControllerProvider =
    StateNotifierProvider<AdminServiceController, AdminServiceState>(
      (ref) => AdminServiceController(AdminServiceApi()),
    );

class AdminServiceState {
  const AdminServiceState({
    this.loading = true,
    this.saving = false,
    this.categories = const [],
    this.providers = const [],
    this.offers = const [],
    this.requests = const [],
    this.providerPage = 1,
    this.providerTotal = 0,
    this.offerPage = 1,
    this.offerTotal = 0,
    this.requestPage = 1,
    this.requestTotal = 0,
    this.error,
  });
  final bool loading, saving;
  final List<AdminServiceCategory> categories;
  final List<AdminServiceProvider> providers;
  final List<AdminServiceOffer> offers;
  final List<AdminServiceRequest> requests;
  final int providerPage,
      providerTotal,
      offerPage,
      offerTotal,
      requestPage,
      requestTotal;
  final String? error;
  AdminServiceState copyWith({
    bool? loading,
    bool? saving,
    List<AdminServiceCategory>? categories,
    List<AdminServiceProvider>? providers,
    List<AdminServiceOffer>? offers,
    List<AdminServiceRequest>? requests,
    int? providerPage,
    int? providerTotal,
    int? offerPage,
    int? offerTotal,
    int? requestPage,
    int? requestTotal,
    String? error,
    bool clearError = false,
  }) => AdminServiceState(
    loading: loading ?? this.loading,
    saving: saving ?? this.saving,
    categories: categories ?? this.categories,
    providers: providers ?? this.providers,
    offers: offers ?? this.offers,
    requests: requests ?? this.requests,
    providerPage: providerPage ?? this.providerPage,
    providerTotal: providerTotal ?? this.providerTotal,
    offerPage: offerPage ?? this.offerPage,
    offerTotal: offerTotal ?? this.offerTotal,
    requestPage: requestPage ?? this.requestPage,
    requestTotal: requestTotal ?? this.requestTotal,
    error: clearError ? null : error ?? this.error,
  );
}

class AdminServiceController extends StateNotifier<AdminServiceState> {
  AdminServiceController(this.api) : super(const AdminServiceState());
  final AdminServiceApi api;
  Future<void> load() async {
    state = state.copyWith(loading: true, clearError: true);
    try {
      final r = await Future.wait([
        api.categories(),
        api.providers(),
        api.offers(),
        api.requests(),
      ]);
      final p = r[1] as AdminServicePage<AdminServiceProvider>,
          o = r[2] as AdminServicePage<AdminServiceOffer>,
          q = r[3] as AdminServicePage<AdminServiceRequest>;
      state = state.copyWith(
        loading: false,
        categories: r[0] as List<AdminServiceCategory>,
        providers: p.items,
        providerPage: p.page,
        providerTotal: p.total,
        offers: o.items,
        offerPage: o.page,
        offerTotal: o.total,
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
      if (kind == 'provider') {
        final r = await api.providers(page: page);
        state = state.copyWith(
          saving: false,
          providers: r.items,
          providerPage: r.page,
          providerTotal: r.total,
        );
      } else if (kind == 'offer') {
        final r = await api.offers(page: page);
        state = state.copyWith(
          saving: false,
          offers: r.items,
          offerPage: r.page,
          offerTotal: r.total,
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

  Future<bool> saveCategory(int? id, Map<String, dynamic> data) async =>
      _action(() async {
        await api.saveCategory(id: id, data: data);
        state = state.copyWith(categories: await api.categories());
      });
  Future<bool> moderate(
    String kind,
    int id,
    String status,
    String? note,
  ) async => _action(() async {
    if (kind == 'provider') {
      await api.providerStatus(id, status, note);
      final r = await api.providers(page: state.providerPage);
      state = state.copyWith(providers: r.items);
    } else if (kind == 'offer') {
      await api.offerStatus(id, status, note);
      final r = await api.offers(page: state.offerPage);
      state = state.copyWith(offers: r.items);
    } else {
      await api.requestStatus(id, status, note);
      final r = await api.requests(page: state.requestPage);
      state = state.copyWith(requests: r.items);
    }
  });
  Future<AdminServiceRequest?> detail(int id) async {
    state = state.copyWith(saving: true, clearError: true);
    try {
      final v = await api.requestDetail(id);
      state = state.copyWith(saving: false);
      return v;
    } catch (e) {
      _fail(e);
      return null;
    }
  }

  Future<bool> confirmCompletion(int id) => _action(() async {
    await api.confirmRequestCompletion(id);
    final r = await api.requests(page: state.requestPage);
    state = state.copyWith(requests: r.items);
  });

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
    final m =
        e is AdminServiceApiException
            ? e.error.message
            : 'خطا در دریافت اطلاعات خدمات';
    state = state.copyWith(loading: loading, saving: false, error: m);
  }
}
