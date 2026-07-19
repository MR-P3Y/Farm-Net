import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/rental_models.dart';
import '../state/rental_discovery_controller.dart';

class RentalEquipmentListScreen extends ConsumerStatefulWidget {
  const RentalEquipmentListScreen({super.key});
  @override
  ConsumerState<RentalEquipmentListScreen> createState() =>
      _RentalEquipmentListScreenState();
}

class _RentalEquipmentListScreenState
    extends ConsumerState<RentalEquipmentListScreen> {
  final _search = TextEditingController();
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(rentalDiscoveryControllerProvider.notifier).load(),
    );
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(rentalDiscoveryControllerProvider);
    final controller = ref.read(rentalDiscoveryControllerProvider.notifier);
    return Scaffold(
      appBar: const FarmAppBar(title: 'اجاره تجهیزات کشاورزی'),
      body:
          state.isLoading
              ? const FarmLoadingView()
              : RefreshIndicator(
                onRefresh: controller.load,
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    TextField(
                      controller: _search,
                      decoration: InputDecoration(
                        labelText: 'جست‌وجوی تجهیزات',
                        prefixIcon: const Icon(Icons.search),
                        suffixIcon: IconButton(
                          onPressed:
                              () => controller.apply(
                                query: _search.text,
                                categoryId: state.categoryId,
                                provinceId: state.provinceId,
                                cityId: state.cityId,
                                operatorMode: state.operatorMode,
                              ),
                          icon: const Icon(Icons.arrow_forward),
                        ),
                      ),
                      onSubmitted:
                          (value) => controller.apply(
                            query: value,
                            categoryId: state.categoryId,
                            provinceId: state.provinceId,
                            cityId: state.cityId,
                            operatorMode: state.operatorMode,
                          ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _Filter<int>(
                          label: 'دسته‌بندی',
                          value: state.categoryId,
                          items:
                              state.categories
                                  .map(
                                    (item) => DropdownMenuItem(
                                      value: item.id,
                                      child: Text(item.title),
                                    ),
                                  )
                                  .toList(),
                          onChanged:
                              (value) => controller.apply(
                                query: state.query,
                                categoryId: value,
                                provinceId: state.provinceId,
                                cityId: state.cityId,
                                operatorMode: state.operatorMode,
                              ),
                        ),
                        _Filter<int>(
                          label: 'استان',
                          value: state.provinceId,
                          items:
                              state.provinces
                                  .map(
                                    (item) => DropdownMenuItem(
                                      value: item.id,
                                      child: Text(item.name),
                                    ),
                                  )
                                  .toList(),
                          onChanged: (value) async {
                            await controller.selectProvince(value);
                            final next = ref.read(
                              rentalDiscoveryControllerProvider,
                            );
                            await controller.apply(
                              query: next.query,
                              categoryId: next.categoryId,
                              provinceId: value,
                              cityId: null,
                              operatorMode: next.operatorMode,
                            );
                          },
                        ),
                        _Filter<int>(
                          label: 'شهر',
                          value: state.cityId,
                          items:
                              state.cities
                                  .map(
                                    (item) => DropdownMenuItem(
                                      value: item.id,
                                      child: Text(item.name),
                                    ),
                                  )
                                  .toList(),
                          onChanged:
                              state.provinceId == null
                                  ? null
                                  : (value) => controller.apply(
                                    query: state.query,
                                    categoryId: state.categoryId,
                                    provinceId: state.provinceId,
                                    cityId: value,
                                    operatorMode: state.operatorMode,
                                  ),
                        ),
                        _Filter<String>(
                          label: 'اپراتور',
                          value: state.operatorMode,
                          items: const [
                            DropdownMenuItem(
                              value: 'with_operator',
                              child: Text('همراه اپراتور'),
                            ),
                            DropdownMenuItem(
                              value: 'without_operator',
                              child: Text('بدون اپراتور'),
                            ),
                            DropdownMenuItem(
                              value: 'either',
                              child: Text('هر دو حالت'),
                            ),
                          ],
                          onChanged:
                              (value) => controller.apply(
                                query: state.query,
                                categoryId: state.categoryId,
                                provinceId: state.provinceId,
                                cityId: state.cityId,
                                operatorMode: value,
                              ),
                        ),
                      ],
                    ),
                    if (state.hasFilters)
                      TextButton.icon(
                        onPressed: () {
                          _search.clear();
                          controller.clear();
                        },
                        icon: const Icon(Icons.clear_all),
                        label: const Text('پاک‌کردن فیلترها'),
                      ),
                    if (state.isFiltering) const LinearProgressIndicator(),
                    if (state.errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          children: [
                            Text(
                              state.errorMessage!,
                              textAlign: TextAlign.center,
                            ),
                            TextButton(
                              onPressed: controller.load,
                              child: const Text('تلاش دوباره'),
                            ),
                          ],
                        ),
                      )
                    else if (state.equipment.isEmpty)
                      const SizedBox(
                        height: 240,
                        child: FarmEmptyView(
                          message: 'تجهیزی با این شرایط پیدا نشد.',
                        ),
                      )
                    else
                      ...state.equipment.map(
                        (item) => _EquipmentCard(equipment: item),
                      ),
                  ],
                ),
              ),
    );
  }
}

class _Filter<T> extends StatelessWidget {
  const _Filter({
    required this.label,
    required this.value,
    required this.items,
    required this.onChanged,
  });
  final String label;
  final T? value;
  final List<DropdownMenuItem<T>> items;
  final ValueChanged<T?>? onChanged;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: 180,
    child: DropdownButtonFormField<T>(
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: [
        DropdownMenuItem<T>(value: null, child: const Text('همه')),
        ...items,
      ],
      onChanged: onChanged,
    ),
  );
}

class _EquipmentCard extends StatelessWidget {
  const _EquipmentCard({required this.equipment});
  final RentalEquipment equipment;
  @override
  Widget build(BuildContext context) {
    final image = absoluteApiUrl(equipment.primaryMedia?.publicUrl);
    return Card(
      margin: const EdgeInsets.only(top: 12),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/rentals/equipment/${equipment.id}'),
        child: Row(
          children: [
            SizedBox(
              width: 120,
              height: 120,
              child:
                  image == null
                      ? const ColoredBox(
                        color: Color(0xffeeeeee),
                        child: Icon(Icons.agriculture, size: 42),
                      )
                      : Image.network(
                        image,
                        fit: BoxFit.cover,
                        errorBuilder:
                            (_, _, _) =>
                                const Icon(Icons.broken_image_outlined),
                      ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      equipment.title,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    if (equipment.category != null)
                      Text(equipment.category!.title),
                    Text(rentalOperatorLabel(equipment.operatorMode)),
                    if ((equipment.lessorDisplayName ?? '').isNotEmpty)
                      Text('موجر: ${equipment.lessorDisplayName}'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
