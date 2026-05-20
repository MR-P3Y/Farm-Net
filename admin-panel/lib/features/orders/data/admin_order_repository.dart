import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'admin_order_api.dart';
import 'admin_order_models.dart';

final adminOrderRepositoryProvider = Provider<AdminOrderRepository>((ref) {
  return AdminOrderRepository(api: AdminOrderApi());
});

class AdminOrderRepository {
  AdminOrderRepository({required AdminOrderApi api}) : _api = api;

  final AdminOrderApi _api;

  Future<List<AdminOrder>> listOrders({
    String? status,
    String? paymentStatus,
    int? storeId,
    int? buyerUserId,
  }) {
    return _api.listOrders(
      status: status,
      paymentStatus: paymentStatus,
      storeId: storeId,
      buyerUserId: buyerUserId,
    );
  }

  Future<AdminOrder> getOrder(int orderId) {
    return _api.getOrder(orderId);
  }

  Future<AdminOrder> updateStatus({
    required int orderId,
    required String status,
    String? adminNote,
  }) {
    return _api.updateStatus(
      orderId: orderId,
      status: status,
      adminNote: adminNote,
    );
  }
}
