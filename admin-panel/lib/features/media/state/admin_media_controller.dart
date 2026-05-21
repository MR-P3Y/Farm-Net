import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_media_api.dart';
import '../data/admin_media_repository.dart';
import 'admin_media_state.dart';

final adminMediaControllerProvider =
    StateNotifierProvider<AdminMediaController, AdminMediaState>((ref) {
      return AdminMediaController(
        repository: ref.watch(adminMediaRepositoryProvider),
      );
    });

class AdminMediaController extends StateNotifier<AdminMediaState> {
  AdminMediaController({required AdminMediaRepository repository})
    : _repository = repository,
      super(AdminMediaState.initial());

  final AdminMediaRepository _repository;

  Future<void> load({
    String? purpose,
    String? visibility,
    String? status,
  }) async {
    state = state.copyWith(
      isLoading: true,
      purposeFilter: purpose,
      visibilityFilter: visibility,
      statusFilter: status,
      clearError: true,
    );

    try {
      final items = await _repository.listMedia(
        purpose: purpose,
        visibility: visibility,
        status: status,
      );

      state = state.copyWith(isLoading: false, items: items);
    } on AdminMediaApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت فایل‌ها',
      );
    }
  }

  Future<void> loadDetail(String fileKey) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final item = await _repository.getMedia(fileKey);
      state = state.copyWith(isSaving: false, selected: item);
    } on AdminMediaApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در دریافت جزئیات فایل',
      );
    }
  }

  Future<bool> updateStatus({
    required String fileKey,
    required String status,
    String? description,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final updated = await _repository.updateStatus(
        fileKey: fileKey,
        status: status,
        description: description,
      );
      final items =
          state.items
              .map((item) => item.fileKey == updated.fileKey ? updated : item)
              .toList();

      state = state.copyWith(isSaving: false, selected: updated, items: items);

      return true;
    } on AdminMediaApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر وضعیت فایل',
      );
      return false;
    }
  }
}
