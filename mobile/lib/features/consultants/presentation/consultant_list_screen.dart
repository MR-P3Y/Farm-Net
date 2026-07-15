import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
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
  bool _loaded = false;

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
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantListControllerProvider);

    return Scaffold(
      appBar: const FarmAppBar(title: 'مشاوران کشاورزی'),
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
                      _SearchBox(
                        controller: _searchController,
                        onSearch: _search,
                        onClear: _clearFilters,
                      ),
                      SizedBox(height: r.v(12)),
                      _SpecialtyChips(
                        specialties: state.specialties,
                        selectedSpecialtyId: state.selectedSpecialtyId,
                        onSelected: (specialtyId) {
                          ref
                              .read(consultantListControllerProvider.notifier)
                              .filterBySpecialty(specialtyId);
                        },
                      ),
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
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      SizedBox(height: r.v(120)),
                                      const FarmEmptyView(
                                        message:
                                            'مشاوری با این فیلترها پیدا نشد.',
                                      ),
                                    ],
                                  )
                                  : ListView.separated(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: state.consultants.length,
                                    separatorBuilder:
                                        (_, __) => SizedBox(height: r.v(10)),
                                    itemBuilder: (context, index) {
                                      final consultant =
                                          state.consultants[index];
                                      return _ConsultantCard(
                                        consultant: consultant,
                                      );
                                    },
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
}

class _SearchBox extends StatelessWidget {
  const _SearchBox({
    required this.controller,
    required this.onSearch,
    required this.onClear,
  });

  final TextEditingController controller;
  final VoidCallback onSearch;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      textInputAction: TextInputAction.search,
      onSubmitted: (_) => onSearch(),
      decoration: InputDecoration(
        hintText: 'جست‌وجوی نام، تخصص یا شهر',
        prefixIcon: const Icon(Icons.search),
        suffixIcon: SizedBox(
          width: 96,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                tooltip: 'پاک کردن',
                onPressed: onClear,
                icon: const Icon(Icons.close),
              ),
              IconButton(
                tooltip: 'جست‌وجو',
                onPressed: onSearch,
                icon: const Icon(Icons.arrow_forward),
              ),
            ],
          ),
        ),
        border: const OutlineInputBorder(),
      ),
    );
  }
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
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          Padding(
            padding: const EdgeInsetsDirectional.only(end: 8),
            child: ChoiceChip(
              label: const Text('همه'),
              selected: selectedSpecialtyId == null,
              onSelected: (_) => onSelected(null),
            ),
          ),
          ...specialties.map(
            (specialty) => Padding(
              padding: const EdgeInsetsDirectional.only(end: 8),
              child: ChoiceChip(
                label: Text(specialty.title),
                selected: selectedSpecialtyId == specialty.id,
                onSelected: (_) => onSelected(specialty.id),
              ),
            ),
          ),
        ],
      ),
    );
  }
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

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/consultants/${consultant.id}'),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _ConsultantAvatar(url: avatarUrl),
              const SizedBox(width: 12),
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
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      children: [
                        _InfoChip(
                          icon: Icons.star_rounded,
                          label:
                              'امتیاز ${toPersianDigits(consultant.ratingAverage.toStringAsFixed(1))}',
                        ),
                        _InfoChip(
                          icon: Icons.rate_review_outlined,
                          label:
                              '${toPersianDigits(consultant.reviewsCount)} نظر',
                        ),
                        _InfoChip(
                          icon: Icons.place_outlined,
                          label: consultant.locationText,
                        ),
                        if (consultant.experienceYears != null)
                          _InfoChip(
                            icon: Icons.work_outline,
                            label:
                                '${toPersianDigits(consultant.experienceYears)} سال',
                          ),
                      ],
                    ),
                    if (specialties.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children:
                            specialties
                                .map(
                                  (specialty) => Chip(
                                    label: Text(specialty.title),
                                    visualDensity: VisualDensity.compact,
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
}

class _ConsultantAvatar extends StatelessWidget {
  const _ConsultantAvatar({required this.url});

  final String? url;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return SizedBox.square(
      dimension: 58,
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
