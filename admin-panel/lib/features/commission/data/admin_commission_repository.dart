import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_commission_api.dart';
import 'admin_commission_models.dart';

final adminCommissionRepositoryProvider = Provider<AdminCommissionRepository>((
  ref,
) {
  return AdminCommissionRepository(api: AdminCommissionApi());
});

class AdminCommissionRepository {
  AdminCommissionRepository({required AdminCommissionApi api}) : _api = api;

  final AdminCommissionApi _api;

  Future<List<AdminCommissionSetting>> listSettings() {
    return _api.listSettings();
  }

  Future<AdminCommissionSetting> getDefault() {
    return _api.getDefault();
  }

  Future<AdminCommissionSetting> updateDefault({
    required num percent,
    String? description,
  }) {
    return _api.updateDefault(percent: percent, description: description);
  }
}
