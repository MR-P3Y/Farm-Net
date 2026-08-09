import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/favorite_models.dart';
import '../state/favorites_controller.dart';

class FavoritesScreen extends ConsumerStatefulWidget {
  const FavoritesScreen({super.key});

  @override
  ConsumerState<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends ConsumerState<FavoritesScreen> {
  FavoriteSubjectType? _filter;

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() => ref
      .read(favoritesControllerProvider.notifier)
      .loadList(subjectType: _filter);

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(favoritesControllerProvider);
    final l10n = context.l10n;

    return Scaffold(
      appBar: FarmAppBar(title: l10n.tr(fa: 'علاقه‌مندی‌ها', en: 'Favorites')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return RefreshIndicator(
            onRefresh: _load,
            child: CustomScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              slivers: [
                SliverToBoxAdapter(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    padding: r.pagePadding().copyWith(bottom: 4),
                    child: Row(
                      children: [
                        _FilterChip(
                          selected: _filter == null,
                          label: l10n.tr(fa: 'همه', en: 'All'),
                          onSelected: () => _select(null),
                        ),
                        for (final type in FavoriteSubjectType.values)
                          Padding(
                            padding: const EdgeInsetsDirectional.only(start: 8),
                            child: _FilterChip(
                              selected: _filter == type,
                              label: _typeLabel(context, type),
                              onSelected: () => _select(type),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                if (state.isLoadingList && state.items.isEmpty)
                  const SliverFillRemaining(child: FarmLoadingView())
                else if (state.errorMessage != null && state.items.isEmpty)
                  SliverFillRemaining(
                    hasScrollBody: false,
                    child: _MessageState(
                      icon: Icons.cloud_off_outlined,
                      message: l10n.tr(
                        fa: 'دریافت علاقه‌مندی‌ها ناموفق بود.',
                        en: 'Could not load favorites.',
                      ),
                      actionLabel: l10n.retry,
                      onAction: _load,
                    ),
                  )
                else if (state.items.isEmpty)
                  SliverFillRemaining(
                    hasScrollBody: false,
                    child: _MessageState(
                      icon: Icons.favorite_border_rounded,
                      message: l10n.tr(
                        fa: 'هنوز موردی را ذخیره نکرده‌اید.',
                        en: 'You have not saved anything yet.',
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding: r.pagePadding(),
                    sliver: SliverList.separated(
                      itemCount: state.items.length,
                      separatorBuilder: (_, __) => SizedBox(height: r.v(10)),
                      itemBuilder: (context, index) {
                        final item = state.items[index];
                        return _FavoriteCard(
                          item: item,
                          onOpen:
                              item.isAvailable && item.route != null
                                  ? () => context.push(item.route!)
                                  : null,
                          onRemove:
                              () => ref
                                  .read(favoritesControllerProvider.notifier)
                                  .removeItem(item),
                        );
                      },
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _select(FavoriteSubjectType? type) async {
    if (_filter == type) return;
    setState(() => _filter = type);
    await _load();
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.selected,
    required this.label,
    required this.onSelected,
  });

  final bool selected;
  final String label;
  final VoidCallback onSelected;

  @override
  Widget build(BuildContext context) => ChoiceChip(
    selected: selected,
    label: Text(label),
    onSelected: (_) => onSelected(),
  );
}

class _FavoriteCard extends StatelessWidget {
  const _FavoriteCard({
    required this.item,
    required this.onOpen,
    required this.onRemove,
  });

  final FavoriteItem item;
  final VoidCallback? onOpen;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final imageUrl = absoluteApiUrl(item.imageUrl);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onOpen,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                width: 76,
                height: 76,
                clipBehavior: Clip.antiAlias,
                decoration: BoxDecoration(
                  color: colors.primaryContainer,
                  borderRadius: BorderRadius.circular(16),
                ),
                child:
                    imageUrl == null
                        ? Icon(
                          _typeIcon(item.subjectType),
                          color: colors.primary,
                        )
                        : Image.network(
                          imageUrl,
                          fit: BoxFit.cover,
                          errorBuilder:
                              (_, __, ___) => Icon(
                                _typeIcon(item.subjectType),
                                color: colors.primary,
                              ),
                        ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            item.title ??
                                context.l10n.tr(
                                  fa: 'مورد حذف‌شده',
                                  en: 'Removed item',
                                ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.w800),
                          ),
                        ),
                        IconButton(
                          tooltip: context.l10n.tr(
                            fa: 'حذف از علاقه‌مندی‌ها',
                            en: 'Remove from favorites',
                          ),
                          onPressed: onRemove,
                          icon: const Icon(Icons.favorite_rounded),
                        ),
                      ],
                    ),
                    if ((item.subtitle ?? '').isNotEmpty)
                      Text(
                        item.subtitle!,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(color: colors.onSurfaceVariant),
                      ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        Text(
                          _typeLabel(context, item.subjectType),
                          style: Theme.of(context).textTheme.labelMedium
                              ?.copyWith(color: colors.primary),
                        ),
                        Text(
                          formatLocalizedDate(
                            item.createdAt,
                            locale: Localizations.localeOf(context),
                          ),
                          style: Theme.of(context).textTheme.labelMedium,
                        ),
                        if (!item.isAvailable)
                          Text(
                            context.l10n.tr(
                              fa: 'دیگر در دسترس نیست',
                              en: 'No longer available',
                            ),
                            style: TextStyle(color: colors.error),
                          ),
                      ],
                    ),
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

class _MessageState extends StatelessWidget {
  const _MessageState({
    required this.icon,
    required this.message,
    this.actionLabel,
    this.onAction,
  });

  final IconData icon;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 52),
          const SizedBox(height: 12),
          Text(message, textAlign: TextAlign.center),
          if (onAction != null) ...[
            const SizedBox(height: 12),
            OutlinedButton(onPressed: onAction, child: Text(actionLabel!)),
          ],
        ],
      ),
    ),
  );
}

String _typeLabel(
  BuildContext context,
  FavoriteSubjectType type,
) => switch (type) {
  FavoriteSubjectType.product => context.l10n.tr(fa: 'محصولات', en: 'Products'),
  FavoriteSubjectType.store => context.l10n.tr(fa: 'فروشگاه‌ها', en: 'Stores'),
  FavoriteSubjectType.serviceOffer => context.l10n.tr(
    fa: 'خدمات',
    en: 'Services',
  ),
  FavoriteSubjectType.rentalEquipment => context.l10n.tr(
    fa: 'تجهیزات',
    en: 'Equipment',
  ),
  FavoriteSubjectType.consultant => context.l10n.tr(
    fa: 'مشاوران',
    en: 'Consultants',
  ),
  FavoriteSubjectType.socialPost => context.l10n.tr(fa: 'مطالب', en: 'Posts'),
};

IconData _typeIcon(FavoriteSubjectType type) => switch (type) {
  FavoriteSubjectType.product => Icons.inventory_2_outlined,
  FavoriteSubjectType.store => Icons.storefront_outlined,
  FavoriteSubjectType.serviceOffer => Icons.handyman_outlined,
  FavoriteSubjectType.rentalEquipment => Icons.agriculture_outlined,
  FavoriteSubjectType.consultant => Icons.support_agent_outlined,
  FavoriteSubjectType.socialPost => Icons.article_outlined,
};
