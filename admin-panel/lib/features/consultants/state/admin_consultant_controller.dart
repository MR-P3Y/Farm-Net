import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_consultant_api.dart';
import '../data/admin_consultant_repository.dart';
import 'admin_consultant_state.dart';

final adminConsultantControllerProvider =
    StateNotifierProvider<AdminConsultantController, AdminConsultantState>((
      ref,
    ) {
      return AdminConsultantController(
        repository: ref.watch(adminConsultantRepositoryProvider),
      );
    });

class AdminConsultantController extends StateNotifier<AdminConsultantState> {
  AdminConsultantController({required AdminConsultantRepository repository})
    : _repository = repository,
      super(AdminConsultantState.initial());

  final AdminConsultantRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final specialties = await _repository.listSpecialties();
      final profiles = await _repository.listProfiles(
        status: state.profileStatusFilter,
      );
      final requests = await _repository.listRequests(
        status: state.requestStatusFilter,
      );

      state = state.copyWith(
        isLoading: false,
        specialties: specialties,
        profiles: profiles,
        requests: requests,
      );
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت اطلاعات مشاوران',
      );
    }
  }

  Future<void> searchSpecialties(String query) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final specialties = await _repository.listSpecialties(q: query);
      state = state.copyWith(isSaving: false, specialties: specialties);
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در جستجوی تخصص‌ها',
      );
    }
  }

  Future<void> filterProfiles(String? status) async {
    state = state.copyWith(
      isSaving: true,
      profileStatusFilter: status,
      clearError: true,
    );

    try {
      final profiles = await _repository.listProfiles(status: status);
      state = state.copyWith(isSaving: false, profiles: profiles);
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در فیلتر مشاوران',
      );
    }
  }

  Future<void> filterRequests(String? status) async {
    state = state.copyWith(
      isSaving: true,
      requestStatusFilter: status,
      clearError: true,
    );

    try {
      final requests = await _repository.listRequests(status: status);
      state = state.copyWith(isSaving: false, requests: requests);
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در فیلتر درخواست‌های مشاوره',
      );
    }
  }

  Future<bool> saveSpecialty({
    int? id,
    required String code,
    required String title,
    String? description,
    required int sortOrder,
    required bool isActive,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      if (id == null) {
        await _repository.createSpecialty(
          code: code,
          title: title,
          description: description,
          sortOrder: sortOrder,
          isActive: isActive,
        );
      } else {
        await _repository.updateSpecialty(
          id: id,
          code: code,
          title: title,
          description: description,
          sortOrder: sortOrder,
          isActive: isActive,
        );
      }

      final specialties = await _repository.listSpecialties();
      state = state.copyWith(isSaving: false, specialties: specialties);
      return true;
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ذخیره تخصص',
      );
    }

    return false;
  }

  Future<bool> updateProfileStatus({
    required int id,
    required String status,
    String? note,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repository.updateProfileStatus(id: id, status: status, note: note);
      final profiles = await _repository.listProfiles(
        status: state.profileStatusFilter,
      );
      state = state.copyWith(isSaving: false, profiles: profiles);
      return true;
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت مشاور',
      );
    }

    return false;
  }

  Future<bool> updateRequestStatus({
    required int id,
    required String status,
    String? note,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final selectedRequest = await _repository.updateRequestStatus(
        id: id,
        status: status,
        note: note,
      );
      final requests = await _repository.listRequests(
        status: state.requestStatusFilter,
      );
      state = state.copyWith(
        isSaving: false,
        requests: requests,
        selectedRequest: selectedRequest,
      );
      return true;
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت درخواست مشاوره',
      );
    }

    return false;
  }

  Future<bool> loadRequestDetail(int id) async {
    state = state.copyWith(
      isSaving: true,
      clearError: true,
      clearSelectedRequest: true,
    );

    try {
      final request = await _repository.requestDetail(id);
      state = state.copyWith(isSaving: false, selectedRequest: request);
      return true;
    } on AdminConsultantApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات درخواست مشاوره',
      );
    }

    return false;
  }
}
