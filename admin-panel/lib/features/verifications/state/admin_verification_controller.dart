import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_verification_api.dart';
import '../data/admin_verification_repository.dart';
import 'admin_verification_state.dart';

final adminVerificationControllerProvider =
    StateNotifierProvider<AdminVerificationController, AdminVerificationState>((
      ref,
    ) {
      return AdminVerificationController(
        repository: ref.watch(adminVerificationRepositoryProvider),
      );
    });

class AdminVerificationController
    extends StateNotifier<AdminVerificationState> {
  AdminVerificationController({required AdminVerificationRepository repository})
    : _repository = repository,
      super(AdminVerificationState.initial());

  final AdminVerificationRepository _repository;

  Future<void> load({String? status, String? targetRole}) async {
    state = state.copyWith(
      isLoading: true,
      statusFilter: status,
      targetRoleFilter: targetRole,
      clearStatusFilter: status == null,
      clearTargetRoleFilter: targetRole == null,
      clearError: true,
    );

    try {
      final items = await _repository.listVerifications(
        status: status,
        targetRole: targetRole,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on AdminVerificationApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت درخواست‌های تأیید',
      );
    }
  }

  Future<void> loadDetail(int requestId) async {
    state = state.copyWith(
      isSaving: true,
      clearSelected: true,
      clearError: true,
    );

    try {
      final selected = await _repository.getDetail(requestId);

      state = state.copyWith(isSaving: false, selected: selected);
    } on AdminVerificationApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات درخواست',
      );
    }
  }

  Future<bool> updateStatus({
    required int requestId,
    required String status,
    String? note,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateStatus(
        requestId: requestId,
        status: status,
        note: note,
      );

      final items =
          state.items
              .map((item) => item.id == updated.id ? updated : item)
              .toList();

      state = state.copyWith(isSaving: false, selected: updated, items: items);

      return true;
    } on AdminVerificationApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت درخواست',
      );
      return false;
    }
  }
}
