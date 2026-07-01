import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/consultant_api.dart';
import '../data/consultant_repository.dart';
import 'consultant_list_state.dart';

final consultantListControllerProvider =
    StateNotifierProvider<ConsultantListController, ConsultantListState>((ref) {
      return ConsultantListController(
        repository: ref.watch(consultantRepositoryProvider),
      );
    });

class ConsultantListController extends StateNotifier<ConsultantListState> {
  ConsultantListController({required ConsultantRepository repository})
    : _repository = repository,
      super(ConsultantListState.initial());

  final ConsultantRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final specialties = await _repository.specialties();
      final consultants = await _repository.list(
        specialtyId: state.selectedSpecialtyId,
        query: state.query,
      );

      state = state.copyWith(
        isLoading: false,
        specialties: specialties,
        consultants: consultants,
      );
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'دریافت فهرست مشاوران ناموفق بود.',
      );
    }
  }

  Future<void> refresh() async {
    await _fetchConsultants(
      specialtyId: state.selectedSpecialtyId,
      query: state.query,
    );
  }

  Future<void> filterBySpecialty(int? specialtyId) async {
    await _fetchConsultants(specialtyId: specialtyId, query: state.query);
  }

  Future<void> search(String query) async {
    await _fetchConsultants(
      specialtyId: state.selectedSpecialtyId,
      query: query.trim(),
    );
  }

  Future<void> clearFilters() async {
    await _fetchConsultants(specialtyId: null, query: '');
  }

  Future<void> _fetchConsultants({
    required int? specialtyId,
    required String query,
  }) async {
    state = state.copyWith(
      isSaving: true,
      selectedSpecialtyId: specialtyId,
      query: query,
      clearError: true,
    );

    try {
      final consultants = await _repository.list(
        specialtyId: specialtyId,
        query: query,
      );

      state = state.copyWith(isSaving: false, consultants: consultants);
    } on ConsultantApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMessage: e.error.message);
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'جست‌وجوی مشاوران ناموفق بود.',
      );
    }
  }
}
