import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_search_field.dart';
import '../../geo/data/geo_models.dart';
import '../data/consultant_models.dart';
import '../state/consultant_list_controller.dart';

class ConsultantListScreen extends ConsumerStatefulWidget {
  const ConsultantListScreen({super.key});

  @override
  ConsumerState<ConsultantListScreen> createState() =>
      _ConsultantListScreenState();
}

class _ConsultantListScreenState extends ConsumerState<ConsultantListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();
  bool _loaded = false;
  bool _headerCollapsed = false;
  Timer? _debounce;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(consultantListControllerProvider.notifier).load();
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantListControllerProvider);

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'مشاوران کشاورزی',
          en: 'Agricultural consultants',
        ),
        actions: [
          IconButton(
            tooltip: context.l10n.tr(fa: 'درخواست‌های من', en: 'My requests'),
            onPressed: () => context.push('/consultants/requests'),
            icon: const Icon(Icons.assignment_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            if (state.isLoading) {
              return const FarmLoadingView();
            }

            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 220),
                        child:
                            _headerCollapsed
                                ? const SizedBox.shrink()
                                : Column(
                                  key: const ValueKey('consultant-header'),
                                  crossAxisAlignment:
                                      CrossAxisAlignment.stretch,
                                  children: [
                                    _DiscoveryHero(
                                      consultantsCount:
                                          state.consultants.length,
                                      specialtiesCount:
                                          state.specialties.length,
                                      onMyRequests:
                                          () => context.push(
                                            '/consultants/requests',
                                          ),
                                    ),
                                    SizedBox(height: r.v(10)),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            context.l10n.tr(
                                              fa: 'انتخاب تخصص',
                                              en: 'Choose a specialty',
                                            ),
                                            style: Theme.of(
                                              context,
                                            ).textTheme.labelLarge?.copyWith(
                                              fontWeight: FontWeight.w900,
                                            ),
                                          ),
                                        ),
                                        if (state.selectedSpecialtyId != null)
                                          TextButton(
                                            onPressed:
                                                () => ref
                                                    .read(
                                                      consultantListControllerProvider
                                                          .notifier,
                                                    )
                                                    .filterBySpecialty(null),
                                            child: Text(
                                              context.l10n.tr(
                                                fa: 'همه',
                                                en: 'All',
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                    _SpecialtyChips(
                                      specialties: state.specialties,
                                      selectedSpecialtyId:
                                          state.selectedSpecialtyId,
                                      onSelected:
                                          ref
                                              .read(
                                                consultantListControllerProvider
                                                    .notifier,
                                              )
                                              .filterBySpecialty,
                                    ),
                                    SizedBox(height: r.v(10)),
                                  ],
                                ),
                      ),
                      Row(
                        children: [
                          Expanded(
                            child: FarmSearchField(
                              controller: _searchController,
                              onChanged: (value) {
                                _debounce?.cancel();
                                _debounce = Timer(
                                  const Duration(milliseconds: 450),
                                  () =>
                                      value.trim().isEmpty
                                          ? _clearFilters()
                                          : _search(),
                                );
                              },
                              onSubmitted: (_) => _search(),
                              hint: context.l10n.tr(
                                fa: 'نام، تخصص یا شهر',
                                en: 'Name, specialty, or city',
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          _FilterMenu(
                            sort: state.sort,
                            specialties: state.specialties,
                            selectedSpecialtyId: state.selectedSpecialtyId,
                            provinces: state.provinces,
                            cities: state.cities,
                            provinceId: state.provinceId,
                            cityId: state.cityId,
                            loadCities:
                                ref
                                    .read(
                                      consultantListControllerProvider.notifier,
                                    )
                                    .loadCities,
                            onApply:
                                ({
                                  required specialtyId,
                                  required provinceId,
                                  required cityId,
                                  required sort,
                                }) => ref
                                    .read(
                                      consultantListControllerProvider.notifier,
                                    )
                                    .applyFilters(
                                      specialtyId: specialtyId,
                                      provinceId: provinceId,
                                      cityId: cityId,
                                      sort: sort,
                                    ),
                            onClear:
                                ref
                                    .read(
                                      consultantListControllerProvider.notifier,
                                    )
                                    .clearDiscoveryFilters,
                          ),
                        ],
                      ),
                      if (state.selectedSpecialtyId != null ||
                          state.provinceId != null ||
                          state.cityId != null ||
                          state.sort != 'rating') ...[
                        const SizedBox(height: 7),
                        Align(
                          alignment: AlignmentDirectional.centerStart,
                          child: ActionChip(
                            avatar: const Icon(
                              Icons.filter_alt_off_outlined,
                              size: 18,
                            ),
                            label: Text(
                              context.l10n.tr(
                                fa: 'پاک‌کردن فیلترها',
                                en: 'Clear filters',
                              ),
                            ),
                            onPressed:
                                ref
                                    .read(
                                      consultantListControllerProvider.notifier,
                                    )
                                    .clearDiscoveryFilters,
                          ),
                        ),
                      ],
                      if (state.isSaving) ...[
                        SizedBox(height: r.v(10)),
                        const LinearProgressIndicator(),
                      ],
                      if (state.errorMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _ErrorBox(message: state.errorMessage!),
                      ],
                      SizedBox(height: r.v(12)),
                      Expanded(
                        child: RefreshIndicator(
                          onRefresh:
                              () =>
                                  ref
                                      .read(
                                        consultantListControllerProvider
                                            .notifier,
                                      )
                                      .refresh(),
                          child:
                              state.consultants.isEmpty
                                  ? ListView(
                                    controller: _scrollController,
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      SizedBox(height: r.v(120)),
                                      FarmEmptyView(
                                        message: context.l10n.tr(
                                          fa: 'مشاوری با این فیلترها پیدا نشد.',
                                          en:
                                              'No consultant matches these filters.',
                                        ),
                                      ),
                                    ],
                                  )
                                  : constraints.maxWidth >= 720
                                  ? GridView.builder(
                                    controller: _scrollController,
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    gridDelegate:
                                        const SliverGridDelegateWithMaxCrossAxisExtent(
                                          maxCrossAxisExtent: 430,
                                          mainAxisExtent: 196,
                                          crossAxisSpacing: 10,
                                          mainAxisSpacing: 10,
                                        ),
                                    itemCount: state.consultants.length,
                                    itemBuilder:
                                        (context, index) => _ConsultantCard(
                                          consultant: state.consultants[index],
                                        ),
                                  )
                                  : ListView.separated(
                                    controller: _scrollController,
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: state.consultants.length,
                                    separatorBuilder:
                                        (_, __) => const SizedBox(height: 8),
                                    itemBuilder:
                                        (context, index) => _ConsultantCard(
                                          consultant: state.consultants[index],
                                        ),
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
      ),
    );
  }

  void _search() {
    ref
        .read(consultantListControllerProvider.notifier)
        .search(_searchController.text);
  }

  void _clearFilters() {
    _searchController.clear();
    ref.read(consultantListControllerProvider.notifier).clearFilters();
  }

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(() {
      final collapsed = _scrollController.offset > 36;
      if (collapsed != _headerCollapsed && mounted) {
        setState(() => _headerCollapsed = collapsed);
      }
    });
  }
}

class _DiscoveryHero extends StatelessWidget {
  const _DiscoveryHero({
    required this.consultantsCount,
    required this.specialtiesCount,
    required this.onMyRequests,
  });

  final int consultantsCount;
  final int specialtiesCount;
  final VoidCallback onMyRequests;

  @override
  Widget build(BuildContext context) => FarmGlassCard(
    borderRadius: 22,
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
    child: Row(
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Theme.of(
              context,
            ).colorScheme.primary.withValues(alpha: 0.14),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(
            Icons.health_and_safety_outlined,
            color: Theme.of(context).colorScheme.primary,
            size: 24,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                context.l10n.tr(
                  fa: 'برای مزرعه‌ات متخصص پیدا کن',
                  en: 'Find an expert for your farm',
                ),
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 5),
              Text(
                context.l10n.tr(
                  fa:
                      '${toPersianDigits(consultantsCount)} مشاور تأییدشده در ${toPersianDigits(specialtiesCount)} تخصص',
                  en:
                      '$consultantsCount approved consultants across $specialtiesCount specialties',
                ),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
        IconButton(
          tooltip: context.l10n.tr(fa: 'درخواست‌های من', en: 'My requests'),
          onPressed: onMyRequests,
          icon: const Icon(Icons.history_rounded),
        ),
      ],
    ),
  );
}

class _FilterMenu extends StatelessWidget {
  const _FilterMenu({
    required this.sort,
    required this.specialties,
    required this.selectedSpecialtyId,
    required this.provinces,
    required this.cities,
    required this.provinceId,
    required this.cityId,
    required this.loadCities,
    required this.onApply,
    required this.onClear,
  });

  final String sort;
  final List<ConsultantSpecialtyModel> specialties;
  final int? selectedSpecialtyId;
  final List<GeoProvince> provinces;
  final List<GeoCity> cities;
  final int? provinceId;
  final int? cityId;
  final Future<List<GeoCity>> Function(int?) loadCities;
  final Future<void> Function({
    required int? specialtyId,
    required int? provinceId,
    required int? cityId,
    required String sort,
  })
  onApply;
  final Future<void> Function() onClear;

  @override
  Widget build(BuildContext context) {
    final active =
        selectedSpecialtyId != null ||
        provinceId != null ||
        cityId != null ||
        sort != 'rating';
    return Badge(
      isLabelVisible: active,
      child: IconButton.filledTonal(
        tooltip: context.l10n.tr(
          fa: 'فیلتر و مرتب‌سازی',
          en: 'Filter and sort',
        ),
        onPressed: () => _open(context),
        icon: const Icon(Icons.tune_rounded),
      ),
    );
  }

  Future<void> _open(BuildContext context) async {
    var draftSpecialty = selectedSpecialtyId;
    var draftProvince = provinceId;
    var draftCity = cityId;
    var draftSort = sort;
    var draftCities = cities;
    await showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder:
          (sheetContext) => StatefulBuilder(
            builder:
                (context, setSheetState) => SafeArea(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          context.l10n.tr(
                            fa: 'فیلتر مشاوران',
                            en: 'Filter consultants',
                          ),
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 18),
                        Text(
                          context.l10n.tr(fa: 'حوزه تخصصی', en: 'Specialty'),
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 5,
                          runSpacing: 5,
                          children: [
                            ChoiceChip(
                              label: Text(
                                context.l10n.tr(fa: 'همه', en: 'All'),
                              ),
                              selected: draftSpecialty == null,
                              visualDensity: VisualDensity.compact,
                              onSelected:
                                  (_) => setSheetState(
                                    () => draftSpecialty = null,
                                  ),
                            ),
                            ...specialties.map(
                              (item) => ChoiceChip(
                                label: Text(item.title),
                                selected: draftSpecialty == item.id,
                                visualDensity: VisualDensity.compact,
                                labelStyle:
                                    Theme.of(context).textTheme.labelSmall,
                                onSelected:
                                    (_) => setSheetState(
                                      () => draftSpecialty = item.id,
                                    ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        Text(
                          context.l10n.tr(
                            fa: 'منطقه جغرافیایی',
                            en: 'Location',
                          ),
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: 8),
                        DropdownButtonFormField<int?>(
                          initialValue: draftProvince,
                          decoration: InputDecoration(
                            labelText: context.l10n.tr(
                              fa: 'استان',
                              en: 'Province',
                            ),
                          ),
                          items: [
                            DropdownMenuItem<int?>(
                              value: null,
                              child: Text(
                                context.l10n.tr(
                                  fa: 'همه استان‌ها',
                                  en: 'All provinces',
                                ),
                              ),
                            ),
                            ...provinces.map(
                              (item) => DropdownMenuItem<int?>(
                                value: item.id,
                                child: Text(item.name),
                              ),
                            ),
                          ],
                          onChanged: (value) async {
                            final loaded = await loadCities(value);
                            if (!sheetContext.mounted) return;
                            setSheetState(() {
                              draftProvince = value;
                              draftCity = null;
                              draftCities = loaded;
                            });
                          },
                        ),
                        if (draftProvince != null) ...[
                          const SizedBox(height: 10),
                          DropdownButtonFormField<int?>(
                            initialValue: draftCity,
                            decoration: InputDecoration(
                              labelText: context.l10n.tr(fa: 'شهر', en: 'City'),
                            ),
                            items: [
                              DropdownMenuItem<int?>(
                                value: null,
                                child: Text(
                                  context.l10n.tr(
                                    fa: 'همه شهرها',
                                    en: 'All cities',
                                  ),
                                ),
                              ),
                              ...draftCities.map(
                                (item) => DropdownMenuItem<int?>(
                                  value: item.id,
                                  child: Text(item.name),
                                ),
                              ),
                            ],
                            onChanged:
                                (value) =>
                                    setSheetState(() => draftCity = value),
                          ),
                        ],
                        const SizedBox(height: 20),
                        Text(
                          context.l10n.tr(fa: 'مرتب‌سازی', en: 'Sort by'),
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        _SortTile(
                          label: context.l10n.tr(
                            fa: 'بالاترین امتیاز',
                            en: 'Highest rated',
                          ),
                          selected: draftSort == 'rating',
                          onTap:
                              () => setSheetState(() => draftSort = 'rating'),
                        ),
                        _SortTile(
                          label: context.l10n.tr(fa: 'جدیدترین', en: 'Newest'),
                          selected: draftSort == 'newest',
                          onTap:
                              () => setSheetState(() => draftSort = 'newest'),
                        ),
                        _SortTile(
                          label: context.l10n.tr(
                            fa: 'مرتبط‌ترین',
                            en: 'Most relevant',
                          ),
                          selected: draftSort == 'relevance',
                          onTap:
                              () =>
                                  setSheetState(() => draftSort = 'relevance'),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton(
                                onPressed: () async {
                                  await onClear();
                                  if (sheetContext.mounted) {
                                    Navigator.pop(sheetContext);
                                  }
                                },
                                child: FittedBox(
                                  fit: BoxFit.scaleDown,
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(
                                        Icons.filter_alt_off_outlined,
                                        size: 19,
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        context.l10n.tr(
                                          fa: 'پاک‌کردن',
                                          en: 'Clear',
                                        ),
                                        maxLines: 1,
                                        softWrap: false,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: FilledButton(
                                onPressed: () async {
                                  await onApply(
                                    specialtyId: draftSpecialty,
                                    provinceId: draftProvince,
                                    cityId: draftCity,
                                    sort: draftSort,
                                  );
                                  if (sheetContext.mounted) {
                                    Navigator.pop(sheetContext);
                                  }
                                },
                                child: FittedBox(
                                  fit: BoxFit.scaleDown,
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(Icons.check_rounded, size: 20),
                                      const SizedBox(width: 7),
                                      Text(
                                        context.l10n.tr(
                                          fa: 'اعمال فیلتر',
                                          en: 'Apply filters',
                                        ),
                                        maxLines: 1,
                                        softWrap: false,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
          ),
    );
  }
}

class _SortTile extends StatelessWidget {
  const _SortTile({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => ListTile(
    dense: true,
    contentPadding: EdgeInsets.zero,
    onTap: onTap,
    title: Text(label),
    trailing:
        selected
            ? Icon(
              Icons.check_circle,
              color: Theme.of(context).colorScheme.primary,
            )
            : const Icon(Icons.circle_outlined),
  );
}

class _SpecialtyChips extends StatelessWidget {
  const _SpecialtyChips({
    required this.specialties,
    required this.selectedSpecialtyId,
    required this.onSelected,
  });

  final List<ConsultantSpecialtyModel> specialties;
  final int? selectedSpecialtyId;
  final ValueChanged<int?> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 84,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          ...specialties.map(
            (specialty) => Padding(
              padding: const EdgeInsetsDirectional.only(end: 8),
              child: _SpecialtyCard(
                specialty: specialty,
                selected: selectedSpecialtyId == specialty.id,
                onTap: () => onSelected(specialty.id),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SpecialtyCard extends StatelessWidget {
  const _SpecialtyCard({
    required this.specialty,
    required this.selected,
    required this.onTap,
  });

  final ConsultantSpecialtyModel specialty;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return SizedBox(
      width: 112,
      child: Material(
        color:
            selected
                ? colors.primaryContainer.withValues(alpha: .82)
                : colors.surfaceContainerHighest.withValues(alpha: .45),
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(18),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 7),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                color: selected ? colors.primary : colors.outlineVariant,
                width: selected ? 1.5 : 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(_specialtyIcon(specialty.code), size: 19),
                const SizedBox(height: 4),
                Expanded(
                  child: Text(
                    specialty.title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                      height: 1.25,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  IconData _specialtyIcon(String code) => switch (code) {
    'plant-nutrition' => Icons.eco_outlined,
    'plant-diseases' => Icons.healing_outlined,
    'pest-management' => Icons.pest_control_outlined,
    'soil-irrigation' => Icons.water_drop_outlined,
    'horticulture' => Icons.park_outlined,
    'field-crops' => Icons.grass_outlined,
    'livestock-poultry' => Icons.pets_outlined,
    'farm-mechanization' => Icons.agriculture_outlined,
    _ => Icons.support_agent_outlined,
  };
}

class _ConsultantCard extends StatelessWidget {
  const _ConsultantCard({required this.consultant});

  final ConsultantProfileModel consultant;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final avatarUrl = absoluteApiUrl(consultant.avatarUrl);
    final specialties = consultant.specialties.take(3).toList();

    return FarmGlassCard(
      borderRadius: 24,
      padding: EdgeInsets.zero,
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: () => context.push('/consultants/${consultant.id}'),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _ConsultantAvatar(url: avatarUrl),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            consultant.resolvedName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.titleMedium,
                          ),
                        ),
                        if (consultant.isVerified)
                          Icon(Icons.verified, size: 20, color: colors.primary),
                      ],
                    ),
                    if ((consultant.title ?? '').trim().isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        consultant.title!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodyMedium,
                      ),
                    ],
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      children: [
                        _InfoChip(
                          icon: Icons.star_rounded,
                          label: context.l10n.tr(
                            fa:
                                'امتیاز ${toPersianDigits(consultant.ratingAverage.toStringAsFixed(1))}',
                            en:
                                'Rating ${consultant.ratingAverage.toStringAsFixed(1)}',
                          ),
                        ),
                        _InfoChip(
                          icon: Icons.rate_review_outlined,
                          label: context.l10n.tr(
                            fa: '${toPersianDigits(consultant.reviewsCount)} نظر',
                            en: '${consultant.reviewsCount} reviews',
                          ),
                        ),
                        _InfoChip(
                          icon: Icons.place_outlined,
                          label: _location(context, consultant),
                        ),
                        if (consultant.experienceYears != null)
                          _InfoChip(
                            icon: Icons.work_outline,
                            label: context.l10n.tr(
                              fa:
                                  '${toPersianDigits(consultant.experienceYears)} سال',
                              en: '${consultant.experienceYears} years',
                            ),
                          ),
                      ],
                    ),
                    if (specialties.isNotEmpty) ...[
                      const SizedBox(height: 7),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children:
                            specialties
                                .map(
                                  (specialty) => Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 3,
                                    ),
                                    decoration: BoxDecoration(
                                      color: colors.primaryContainer.withValues(
                                        alpha: 0.55,
                                      ),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Text(
                                      specialty.title,
                                      style: theme.textTheme.labelSmall,
                                    ),
                                  ),
                                )
                                .toList(),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _location(BuildContext context, ConsultantProfileModel value) {
    final parts =
        [value.cityName, value.provinceName]
            .where((item) => item?.trim().isNotEmpty == true)
            .cast<String>()
            .toList();
    return parts.isEmpty
        ? context.l10n.tr(fa: 'موقعیت ثبت نشده', en: 'Location unavailable')
        : parts.join(context.l10n.isFa ? '، ' : ', ');
  }
}

class _ConsultantAvatar extends StatelessWidget {
  const _ConsultantAvatar({required this.url});

  final String? url;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return SizedBox.square(
      dimension: 50,
      child: DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: colors.primaryContainer,
        ),
        child: ClipOval(
          child:
              url == null
                  ? Icon(
                    Icons.support_agent_outlined,
                    color: colors.onPrimaryContainer,
                  )
                  : Image.network(
                    url!,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) {
                      return Icon(
                        Icons.support_agent_outlined,
                        color: colors.onPrimaryContainer,
                      );
                    },
                  ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 18),
      label: Text(label),
      visualDensity: VisualDensity.compact,
    );
  }
}

class _ErrorBox extends StatelessWidget {
  const _ErrorBox({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.errorContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(message, style: TextStyle(color: colors.onErrorContainer)),
      ),
    );
  }
}
