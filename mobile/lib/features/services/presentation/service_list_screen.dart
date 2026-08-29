import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:geolocator/geolocator.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_circular_glass_button.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_search_field.dart';
import '../../favorites/data/favorite_models.dart';
import '../../favorites/presentation/favorite_button.dart';
import '../data/service_models.dart';
import '../state/service_discovery_controller.dart';
import '../state/service_discovery_state.dart';
import 'service_map_view.dart';
import 'service_request_badge.dart';
import 'service_ui.dart';

class ServiceListScreen extends ConsumerStatefulWidget {
  const ServiceListScreen({super.key});

  @override
  ConsumerState<ServiceListScreen> createState() => _ServiceListScreenState();
}

class _ServiceListScreenState extends ConsumerState<ServiceListScreen> {
  final _search = TextEditingController();
  Timer? _searchDebounce;
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
    _searchDebounce?.cancel();
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceDiscoveryControllerProvider);
    final controller = ref.read(serviceDiscoveryControllerProvider.notifier);

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'خدمات کشاورزی',
          en: 'Agricultural services',
        ),
        fallbackLocation: '/discover',
        actions: [const MyServiceRequestsAction()],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
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
                physics: const AlwaysScrollableScrollPhysics(),
                padding: r.pagePadding(),
                children: [
                  Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 960),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: FarmSearchField(
                                  controller: _search,
                                  hint: context.l10n.tr(
                                    fa: 'جست‌وجوی خدمات',
                                    en: 'Search services',
                                  ),
                                  onChanged: _onSearchChanged,
                                ),
                              ),
                              SizedBox(width: r.s(10)),
                              FarmCircularGlassButton(
                                icon: Icons.tune_rounded,
                                tooltip: context.l10n.tr(
                                  fa: 'فیلترهای بیشتر',
                                  en: 'More filters',
                                ),
                                onTap: () => _showFilters(context),
                              ),
                            ],
                          ),
                          SizedBox(height: r.v(10)),
                          _SectionTitle(
                            title: context.l10n.tr(
                              fa: 'دسته‌بندی خدمات',
                              en: 'Service categories',
                            ),
                            subtitle: context.l10n.tr(
                              fa: 'برای دسترسی سریع انتخاب کنید',
                              en: 'Choose one for quick access',
                            ),
                          ),
                          const SizedBox(height: 10),
                          ServiceCategoryQuickFilter(
                            categories: state.categories,
                            selectedCategoryId: state.categoryId,
                            enabled: !state.isFiltering,
                            onSelected:
                                (categoryId) => controller.apply(
                                  query: _search.text,
                                  categoryId: categoryId,
                                ),
                          ),
                          SizedBox(height: r.v(12)),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              SegmentedButton<ServiceViewMode>(
                                showSelectedIcon: false,
                                style: const ButtonStyle(
                                  visualDensity: VisualDensity.compact,
                                ),
                                segments: [
                                  ButtonSegment(
                                    value: ServiceViewMode.list,
                                    icon: const Icon(Icons.view_list_rounded),
                                    label: Text(
                                      context.l10n.tr(fa: 'فهرست', en: 'List'),
                                    ),
                                  ),
                                  ButtonSegment(
                                    value: ServiceViewMode.map,
                                    icon: const Icon(Icons.map_outlined),
                                    label: Text(
                                      context.l10n.tr(fa: 'نقشه', en: 'Map'),
                                    ),
                                  ),
                                ],
                                selected: {state.viewMode},
                                onSelectionChanged:
                                    (values) =>
                                        controller.setViewMode(values.first),
                              ),
                              FilledButton.tonalIcon(
                                onPressed:
                                    state.isLocating
                                        ? null
                                        : controller.useCurrentLocation,
                                icon:
                                    state.isLocating
                                        ? const SizedBox.square(
                                          dimension: 18,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                          ),
                                        )
                                        : const Icon(Icons.near_me_outlined),
                                label: Text(
                                  context.l10n.tr(
                                    fa:
                                        state.userLatitude == null
                                            ? 'نزدیک من'
                                            : 'موقعیت فعال',
                                    en:
                                        state.userLatitude == null
                                            ? 'Near me'
                                            : 'Location active',
                                  ),
                                ),
                              ),
                              if (state.hasFilters)
                                IconButton.filledTonal(
                                  tooltip: context.l10n.tr(
                                    fa: 'پاک‌کردن فیلترها',
                                    en: 'Clear filters',
                                  ),
                                  onPressed: () {
                                    _searchDebounce?.cancel();
                                    _search.clear();
                                    controller.clear();
                                  },
                                  icon: const Icon(
                                    Icons.filter_alt_off_rounded,
                                  ),
                                ),
                            ],
                          ),
                          if (state.isFiltering) ...[
                            const SizedBox(height: 6),
                            const LinearProgressIndicator(minHeight: 2),
                          ],
                          SizedBox(height: r.v(10)),
                          _ResultsHeader(count: state.offers.length),
                          SizedBox(height: r.v(8)),
                          if (state.errorMessage != null)
                            Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: Text(
                                state.errorMessage!,
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              ),
                            ),
                          if (state.offers.isEmpty)
                            FarmEmptyView(
                              title: context.l10n.tr(
                                fa: 'خدمتی پیدا نشد',
                                en: 'No services found',
                              ),
                              message: context.l10n.tr(
                                fa:
                                    'فیلترها را تغییر دهید یا دوباره جست‌وجو کنید.',
                                en: 'Change the filters or try another search.',
                              ),
                              actionLabel:
                                  state.hasFilters
                                      ? context.l10n.tr(
                                        fa: 'نمایش همه خدمات',
                                        en: 'Show all services',
                                      )
                                      : null,
                              onAction:
                                  state.hasFilters
                                      ? () {
                                        _search.clear();
                                        controller.clear();
                                      }
                                      : null,
                            )
                          else if (state.viewMode == ServiceViewMode.map)
                            ServiceMapView(
                              offers: state.offers,
                              userLatitude: state.userLatitude,
                              userLongitude: state.userLongitude,
                            )
                          else
                            ...state.offers.map(
                              (offer) => Padding(
                                padding: EdgeInsets.only(bottom: r.v(12)),
                                child: _ServiceCard(
                                  offer: offer,
                                  userLatitude: state.userLatitude,
                                  userLongitude: state.userLongitude,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  void _onSearchChanged(String value) {
    _searchDebounce?.cancel();
    _searchDebounce = Timer(const Duration(milliseconds: 320), () {
      if (!mounted) return;
      ref
          .read(serviceDiscoveryControllerProvider.notifier)
          .apply(query: value.trim());
    });
  }

  DropdownMenuItem<String> _sortItem(
    BuildContext context,
    String value,
    String fa,
    String en,
  ) => DropdownMenuItem(
    value: value,
    child: Text(context.l10n.tr(fa: fa, en: en)),
  );

  Future<void> _showFilters(BuildContext context) async {
    final state = ref.read(serviceDiscoveryControllerProvider);
    final controller = ref.read(serviceDiscoveryControllerProvider.notifier);
    var categoryId = state.categoryId;
    var provinceId = state.provinceId;
    var cityId = state.cityId;
    var pricingType = state.pricingType;
    var sort = state.sort;

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder:
          (sheetContext) => StatefulBuilder(
            builder: (context, setModalState) {
              final latest = ref.watch(serviceDiscoveryControllerProvider);
              return SafeArea(
                child: Padding(
                  padding: EdgeInsets.fromLTRB(
                    20,
                    4,
                    20,
                    MediaQuery.viewInsetsOf(context).bottom + 20,
                  ),
                  child: SingleChildScrollView(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          context.l10n.tr(
                            fa: 'فیلتر خدمات',
                            en: 'Service filters',
                          ),
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<String>(
                          initialValue: sort,
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(
                              fa: 'مرتب‌سازی نتایج',
                              en: 'Sort results',
                            ),
                          ),
                          items: [
                            _sortItem(
                              context,
                              'relevance',
                              'پیشنهادی',
                              'Recommended',
                            ),
                            _sortItem(context, 'newest', 'جدیدترین', 'Newest'),
                            _sortItem(
                              context,
                              'rating',
                              'بیشترین امتیاز',
                              'Top rated',
                            ),
                            _sortItem(
                              context,
                              'price_asc',
                              'کمترین قیمت',
                              'Lowest price',
                            ),
                            _sortItem(
                              context,
                              'price_desc',
                              'بیشترین قیمت',
                              'Highest price',
                            ),
                            if (state.userLatitude != null)
                              _sortItem(
                                context,
                                'distance',
                                'نزدیک‌ترین',
                                'Nearest',
                              ),
                          ],
                          onChanged:
                              (value) =>
                                  setModalState(() => sort = value ?? sort),
                        ),
                        const SizedBox(height: 12),
                        DropdownButtonFormField<int?>(
                          initialValue: categoryId,
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(
                              fa: 'دسته‌بندی',
                              en: 'Category',
                            ),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: null,
                              child: Text(
                                context.l10n.tr(
                                  fa: 'همه دسته‌ها',
                                  en: 'All categories',
                                ),
                              ),
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
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(
                              fa: 'استان',
                              en: 'Province',
                            ),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: null,
                              child: Text(
                                context.l10n.tr(
                                  fa: 'همه استان‌ها',
                                  en: 'All provinces',
                                ),
                              ),
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
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(fa: 'شهر', en: 'City'),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: null,
                              child: Text(
                                context.l10n.tr(
                                  fa: 'همه شهرها',
                                  en: 'All cities',
                                ),
                              ),
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
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(
                              fa: 'شیوه قیمت‌گذاری',
                              en: 'Pricing type',
                            ),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: null,
                              child: Text(
                                context.l10n.tr(
                                  fa: 'همه روش‌ها',
                                  en: 'All pricing types',
                                ),
                              ),
                            ),
                            for (final type in const [
                              'fixed',
                              'hourly',
                              'daily',
                              'hectare',
                              'project',
                              'negotiable',
                            ])
                              DropdownMenuItem(
                                value: type,
                                child: Text(
                                  servicePricingTypeLabel(context, type),
                                ),
                              ),
                          ],
                          onChanged:
                              (value) =>
                                  setModalState(() => pricingType = value),
                        ),
                        const SizedBox(height: 20),
                        FilledButton.icon(
                          onPressed: () {
                            Navigator.pop(sheetContext);
                            controller.apply(
                              query: _search.text,
                              categoryId: categoryId,
                              provinceId: provinceId,
                              cityId: cityId,
                              pricingType: pricingType,
                              sort: sort,
                            );
                          },
                          icon: const Icon(Icons.filter_alt_rounded),
                          label: Text(
                            context.l10n.tr(
                              fa: 'اعمال فیلتر',
                              en: 'Apply filters',
                            ),
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

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: Text(
            title,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
        ),
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

class ServiceCategoryQuickFilter extends StatelessWidget {
  const ServiceCategoryQuickFilter({
    required this.categories,
    required this.selectedCategoryId,
    required this.onSelected,
    this.enabled = true,
    super.key,
  });

  final List<ServiceCategory> categories;
  final int? selectedCategoryId;
  final ValueChanged<int?> onSelected;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 88,
      child: ListView.separated(
        key: const Key('service-category-quick-filter'),
        scrollDirection: Axis.horizontal,
        itemCount: categories.length + 1,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final category = index == 0 ? null : categories[index - 1];
          final id = category?.id;
          final selected = selectedCategoryId == id;
          return _QuickCategoryTile(
            label: category?.title ?? context.l10n.tr(fa: 'همه', en: 'All'),
            icon:
                category == null
                    ? Icons.grid_view_rounded
                    : serviceCategoryIcon(category),
            selected: selected,
            onTap: enabled ? () => onSelected(id) : null,
          );
        },
      ),
    );
  }
}

class _QuickCategoryTile extends StatelessWidget {
  const _QuickCategoryTile({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Semantics(
      button: true,
      selected: selected,
      label: label,
      child: Material(
        color: selected ? colors.primaryContainer : colors.surfaceContainer,
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(18),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            width: 92,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color:
                    selected
                        ? colors.primary
                        : colors.outlineVariant.withValues(alpha: .7),
                width: selected ? 1.5 : 1,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  icon,
                  size: 25,
                  color: selected ? colors.primary : colors.onSurfaceVariant,
                ),
                const SizedBox(height: 7),
                Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: selected ? colors.primary : null,
                    fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ResultsHeader extends StatelessWidget {
  const _ResultsHeader({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    final localizedCount =
        context.l10n.isFa ? toPersianDigits(count) : count.toString();
    return Row(
      children: [
        Expanded(
          child: Text(
            context.l10n.tr(fa: 'خدمات پیشنهادی', en: 'Recommended services'),
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
        ),
        Text(
          context.l10n.tr(
            fa: '$localizedCount نتیجه',
            en: '$localizedCount results',
          ),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

class _ServiceCard extends StatelessWidget {
  const _ServiceCard({
    required this.offer,
    this.userLatitude,
    this.userLongitude,
  });

  final ServiceOffer offer;
  final double? userLatitude;
  final double? userLongitude;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final imageUrl = absoluteApiUrl(offer.primaryMedia?.displayUrl);
    return FarmGlassCard(
      borderRadius: 22,
      padding: EdgeInsets.zero,
      child: InkWell(
        borderRadius: BorderRadius.circular(22),
        onTap: () => context.push('/services/${offer.id}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: SizedBox.square(
                  dimension: 96,
                  child:
                      imageUrl == null
                          ? ColoredBox(
                            color: colors.primaryContainer,
                            child: Icon(
                              serviceCategoryIcon(offer.category),
                              size: 38,
                              color: colors.primary,
                            ),
                          )
                          : Image.network(
                            imageUrl,
                            fit: BoxFit.cover,
                            errorBuilder:
                                (_, __, ___) => ColoredBox(
                                  color: colors.primaryContainer,
                                  child: Icon(
                                    serviceCategoryIcon(offer.category),
                                    color: colors.primary,
                                  ),
                                ),
                          ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (offer.category != null)
                      Text(
                        offer.category!.title,
                        style: Theme.of(
                          context,
                        ).textTheme.labelMedium?.copyWith(
                          color: colors.primary,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    const SizedBox(height: 2),
                    Text(
                      offer.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            serviceProviderName(context, offer.provider),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
                        if (offer.provider?.isVerified == true) ...[
                          const SizedBox(width: 4),
                          Icon(
                            Icons.verified_rounded,
                            size: 16,
                            color: colors.primary,
                          ),
                        ],
                      ],
                    ),
                    if (offer.location.isNotEmpty) ...[
                      const SizedBox(height: 3),
                      Row(
                        children: [
                          Icon(
                            Icons.place_outlined,
                            size: 15,
                            color: colors.onSurfaceVariant,
                          ),
                          const SizedBox(width: 3),
                          Expanded(
                            child: Text(
                              offer.location,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(color: colors.onSurfaceVariant),
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (userLatitude != null &&
                        userLongitude != null &&
                        offer.latitude != null &&
                        offer.longitude != null) ...[
                      const SizedBox(height: 3),
                      Text(
                        context.l10n.tr(
                          fa:
                              '${toPersianDigits((_distanceMeters() / 1000).toStringAsFixed(1))} کیلومتر فاصله',
                          en:
                              '${(_distanceMeters() / 1000).toStringAsFixed(1)} km away',
                        ),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: colors.onSurfaceVariant,
                        ),
                      ),
                    ],
                    const SizedBox(height: 7),
                    Text(
                      servicePriceLabel(context, offer),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: colors.primary,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
              FavoriteIconButton(
                subjectType: FavoriteSubjectType.serviceOffer,
                subjectId: offer.id,
              ),
            ],
          ),
        ),
      ),
    );
  }

  double _distanceMeters() => Geolocator.distanceBetween(
    userLatitude!,
    userLongitude!,
    offer.latitude!,
    offer.longitude!,
  );
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
            label: Text(context.l10n.retry),
          ),
        ],
      ),
    ),
  );
}
