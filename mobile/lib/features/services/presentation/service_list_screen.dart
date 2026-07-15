import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/service_models.dart';
import '../state/service_discovery_controller.dart';

class ServiceListScreen extends ConsumerStatefulWidget {
  const ServiceListScreen({super.key});
  @override
  ConsumerState<ServiceListScreen> createState() => _ServiceListScreenState();
}

class _ServiceListScreenState extends ConsumerState<ServiceListScreen> {
  final _search = TextEditingController();
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(serviceDiscoveryControllerProvider.notifier).load(),
    );
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceDiscoveryControllerProvider);
    final controller = ref.read(serviceDiscoveryControllerProvider.notifier);
    return Scaffold(
      appBar: AppBar(title: const Text('خدمات کشاورزی')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) return const FarmLoadingView();
          if (state.errorMessage != null && state.offers.isEmpty) {
            return _ErrorView(
              message: state.errorMessage!,
              onRetry: controller.load,
            );
          }
          return RefreshIndicator(
            onRefresh: controller.load,
            child: ListView(
              padding: r.pagePadding(),
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _search,
                        decoration: const InputDecoration(
                          hintText: 'جست‌وجوی خدمات',
                          prefixIcon: Icon(Icons.search),
                          border: OutlineInputBorder(),
                        ),
                        onSubmitted: (value) => controller.apply(query: value),
                      ),
                    ),
                    SizedBox(width: r.s(8)),
                    IconButton.filledTonal(
                      tooltip: 'فیلترها',
                      icon: const Icon(Icons.tune),
                      onPressed: () => _showFilters(context),
                    ),
                  ],
                ),
                if (state.hasFilters) ...[
                  SizedBox(height: r.v(8)),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton.icon(
                      onPressed: () {
                        _search.clear();
                        controller.clear();
                      },
                      icon: const Icon(Icons.filter_alt_off),
                      label: const Text('پاک‌کردن فیلترها'),
                    ),
                  ),
                ],
                if (state.isFiltering) const LinearProgressIndicator(),
                SizedBox(height: r.v(16)),
                if (state.errorMessage != null)
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (state.offers.isEmpty)
                  const Padding(
                    padding: EdgeInsets.only(top: 64),
                    child: FarmEmptyView(
                      message: 'خدمتی با این مشخصات پیدا نشد.',
                    ),
                  )
                else
                  ...state.offers.map(
                    (offer) => Padding(
                      padding: EdgeInsets.only(bottom: r.v(12)),
                      child: _ServiceCard(offer: offer),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _showFilters(BuildContext context) async {
    final state = ref.read(serviceDiscoveryControllerProvider);
    final controller = ref.read(serviceDiscoveryControllerProvider.notifier);
    var categoryId = state.categoryId;
    var provinceId = state.provinceId;
    var cityId = state.cityId;
    var pricingType = state.pricingType;
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder:
          (sheetContext) => StatefulBuilder(
            builder: (context, setModalState) {
              final latest = ref.watch(serviceDiscoveryControllerProvider);
              return SafeArea(
                child: Padding(
                  padding: EdgeInsets.fromLTRB(
                    20,
                    20,
                    20,
                    MediaQuery.viewInsetsOf(context).bottom + 20,
                  ),
                  child: SingleChildScrollView(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'فیلتر خدمات',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<int?>(
                          initialValue: categoryId,
                          decoration: const InputDecoration(
                            labelText: 'دسته‌بندی',
                          ),
                          items: [
                            const DropdownMenuItem(
                              value: null,
                              child: Text('همه دسته‌ها'),
                            ),
                            ...latest.categories.map(
                              (item) => DropdownMenuItem(
                                value: item.id,
                                child: Text(item.title),
                              ),
                            ),
                          ],
                          onChanged:
                              (value) =>
                                  setModalState(() => categoryId = value),
                        ),
                        const SizedBox(height: 12),
                        DropdownButtonFormField<int?>(
                          initialValue: provinceId,
                          decoration: const InputDecoration(labelText: 'استان'),
                          items: [
                            const DropdownMenuItem(
                              value: null,
                              child: Text('همه استان‌ها'),
                            ),
                            ...latest.provinces.map(
                              (item) => DropdownMenuItem(
                                value: item.id,
                                child: Text(item.name),
                              ),
                            ),
                          ],
                          onChanged: (value) async {
                            provinceId = value;
                            cityId = null;
                            await controller.selectProvince(value);
                            setModalState(() {});
                          },
                        ),
                        const SizedBox(height: 12),
                        DropdownButtonFormField<int?>(
                          initialValue: cityId,
                          decoration: const InputDecoration(labelText: 'شهر'),
                          items: [
                            const DropdownMenuItem(
                              value: null,
                              child: Text('همه شهرها'),
                            ),
                            ...latest.cities.map(
                              (item) => DropdownMenuItem(
                                value: item.id,
                                child: Text(item.name),
                              ),
                            ),
                          ],
                          onChanged:
                              (value) => setModalState(() => cityId = value),
                        ),
                        const SizedBox(height: 12),
                        DropdownButtonFormField<String?>(
                          initialValue: pricingType,
                          decoration: const InputDecoration(
                            labelText: 'شیوه قیمت‌گذاری',
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: null,
                              child: Text('همه روش‌ها'),
                            ),
                            DropdownMenuItem(
                              value: 'fixed',
                              child: Text('قیمت ثابت'),
                            ),
                            DropdownMenuItem(
                              value: 'hourly',
                              child: Text('ساعتی'),
                            ),
                            DropdownMenuItem(
                              value: 'daily',
                              child: Text('روزانه'),
                            ),
                            DropdownMenuItem(
                              value: 'hectare',
                              child: Text('هکتاری'),
                            ),
                            DropdownMenuItem(
                              value: 'project',
                              child: Text('پروژه‌ای'),
                            ),
                            DropdownMenuItem(
                              value: 'negotiable',
                              child: Text('توافقی'),
                            ),
                          ],
                          onChanged:
                              (value) =>
                                  setModalState(() => pricingType = value),
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: FilledButton(
                            onPressed: () {
                              Navigator.pop(sheetContext);
                              controller.apply(
                                query: _search.text,
                                categoryId: categoryId,
                                provinceId: provinceId,
                                cityId: cityId,
                                pricingType: pricingType,
                              );
                            },
                            child: const Text('اعمال فیلتر'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
    );
  }
}

class _ServiceCard extends StatelessWidget {
  const _ServiceCard({required this.offer});
  final ServiceOffer offer;
  @override
  Widget build(BuildContext context) {
    final imageUrl = absoluteApiUrl(offer.primaryMedia?.displayUrl);
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/services/${offer.id}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: SizedBox.square(
                  dimension: 84,
                  child:
                      imageUrl == null
                          ? const ColoredBox(
                            color: Color(0xFFE8F1E8),
                            child: Icon(Icons.agriculture_outlined),
                          )
                          : Image.network(
                            imageUrl,
                            fit: BoxFit.cover,
                            errorBuilder:
                                (_, __, ___) =>
                                    const Icon(Icons.broken_image_outlined),
                          ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      offer.title,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 4),
                    Text(offer.provider?.resolvedName ?? 'خدمات‌دهنده'),
                    if (offer.location.isNotEmpty) Text(offer.location),
                    const SizedBox(height: 6),
                    Text(
                      _priceLabel(offer),
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_left),
            ],
          ),
        ),
      ),
    );
  }
}

String _priceLabel(ServiceOffer offer) {
  if (offer.pricingType == 'negotiable' || offer.priceAmount == null) {
    return 'قیمت توافقی';
  }
  final mode =
      {
        'fixed': 'ثابت',
        'hourly': 'ساعتی',
        'daily': 'روزانه',
        'hectare': 'هکتاری',
        'project': 'پروژه‌ای',
      }[offer.pricingType];
  return '${offer.priceAmount!.toStringAsFixed(0)} ${offer.currency == 'TOMAN' ? 'تومان' : offer.currency}${mode == null ? '' : ' • $mode'}';
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.cloud_off_outlined, size: 48),
          const SizedBox(height: 12),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('تلاش دوباره'),
          ),
        ],
      ),
    ),
  );
}
