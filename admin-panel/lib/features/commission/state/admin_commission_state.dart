import '../data/admin_commission_models.dart';

class AdminCommissionState {
  const AdminCommissionState({
    required this.isLoading,
    this.isSaving = false,
    this.items = const [],
    this.setting,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<AdminCommissionSetting> items;
  final AdminCommissionSetting? setting;
  final String? errorMessage;

  factory AdminCommissionState.initial() {
    return const AdminCommissionState(isLoading: true);
  }

  AdminCommissionState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<AdminCommissionSetting>? items,
    AdminCommissionSetting? setting,
    String? errorMessage,
    bool clearError = false,
  }) {
    return AdminCommissionState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      items: items ?? this.items,
      setting: setting ?? this.setting,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
