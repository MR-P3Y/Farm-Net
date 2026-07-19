import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'rental_api.dart';
import 'rental_models.dart';

final rentalRepositoryProvider = Provider<RentalRepository>(
  (ref) => RentalRepository(api: RentalApi()),
);

class RentalRepository {
  RentalRepository({required RentalApi api}) : _api = api;
  final RentalApi _api;

  Future<List<RentalCategory>> categories() => _api.categories();
  Future<List<RentalEquipment>> equipment({
    String? query,
    int? categoryId,
    int? provinceId,
    int? cityId,
    String? operatorMode,
  }) => _api.equipment(
    query: query,
    categoryId: categoryId,
    provinceId: provinceId,
    cityId: cityId,
    operatorMode: operatorMode,
  );
  Future<RentalEquipmentDetail> detail(int id) => _api.detail(id);
}
