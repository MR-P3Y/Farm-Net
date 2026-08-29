import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/admin_commission_api.dart';
import '../data/admin_commission_models.dart';
import '../data/admin_commission_repository.dart';
import 'admin_commission_state.dart';

final adminCommissionControllerProvider =
    StateNotifierProvider<AdminCommissionController, AdminCommissionState>((
      ref,
    ) {
      return AdminCommissionController(
        repository: ref.watch(adminCommissionRepositoryProvider),
      );
    });

class AdminCommissionController extends StateNotifier<AdminCommissionState> {
  AdminCommissionController({required AdminCommissionRepository repository})
    : _repository = repository,
      super(AdminCommissionState.initial());

  final AdminCommissionRepository _repository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await Future.wait([
        _repository.listSettings(),
        _repository.getDefault(),
        _repository.listPolicies(),
      ]);
      final policies = result[2] as List<AdminCommissionPolicy>;
      state = state.copyWith(
        isLoading: false,
        items: result[0] as List<AdminCommissionSetting>,
        setting: result[1] as AdminCommissionSetting,
        servicePolicy:
            policies
                .where((item) => item.sourceType == 'service_request')
                .firstOrNull,
      );
    } on AdminCommissionApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت کمیسیون',
      );
    }
  }

  Future<bool> update({required num percent, String? description}) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final setting = await _repository.updateDefault(
        percent: percent,
        description: description,
      );

      final items =
          state.items
              .map((item) => item.id == setting.id ? setting : item)
              .toList();

      state = state.copyWith(isSaving: false, items: items, setting: setting);
      return true;
    } on AdminCommissionApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر کمیسیون',
      );
      return false;
    }
  }

  Future<bool> updateServicePolicy({required num percent}) async {
    state = state.copyWith(isSaving: true, clearError: true);
    try {
      final policy = await _repository.updateServicePolicy(percent: percent);
      state = state.copyWith(isSaving: false, servicePolicy: policy);
      return true;
    } on AdminCommissionApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در تغییر کمیسیون خدمات',
      );
    }
    return false;
  }
}
