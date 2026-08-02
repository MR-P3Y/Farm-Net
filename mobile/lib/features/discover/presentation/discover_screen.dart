import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/theme/app_illustrations.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_glass_card.dart';

class DiscoverScreen extends StatelessWidget {
  const DiscoverScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final entries = _entries(context);
    return Scaffold(
      appBar: FarmAppBar(title: context.l10n.discover, showBack: false),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          final columns =
              r.isDesktop
                  ? 4
                  : r.isTablet
                  ? 3
                  : 2;
          return CustomScrollView(
            slivers: [
              SliverToBoxAdapter(
                child: Padding(
                  padding: r.pagePadding(),
                  child: Text(
                    context.l10n.allServices,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              SliverPadding(
                padding: EdgeInsets.fromLTRB(
                  r.pagePadding().horizontal / 2,
                  0,
                  r.pagePadding().horizontal / 2,
                  AppSpacing.xxl,
                ),
                sliver: SliverGrid.builder(
                  itemCount: entries.length,
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: columns,
                    mainAxisSpacing: AppSpacing.md,
                    crossAxisSpacing: AppSpacing.md,
                    childAspectRatio: r.isMobile ? 1.15 : 1.35,
                  ),
                  itemBuilder:
                      (context, index) => _DiscoverTile(entry: entries[index]),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _DiscoverTile extends StatelessWidget {
  const _DiscoverTile({required this.entry});

  final _DiscoverEntry entry;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Semantics(
      button: true,
      label: entry.label,
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: () => context.push(entry.route),
        child: FarmGlassCard(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: colors.primaryContainer,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(entry.icon, color: colors.onPrimaryContainer),
              ),
              const Spacer(),
              Text(
                entry.label,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

List<_DiscoverEntry> _entries(BuildContext context) => [
  _DiscoverEntry(context.l10n.farms, AppIllustrations.farm, '/farms'),
  _DiscoverEntry(
    context.l10n.tr(fa: 'جعبه‌ابزار مزرعه', en: 'Farm toolbox'),
    Icons.handyman_outlined,
    '/toolbox',
  ),
  _DiscoverEntry(context.l10n.weather, AppIllustrations.weather, '/weather'),
  _DiscoverEntry(
    context.l10n.consultants,
    AppIllustrations.consultant,
    '/consultants',
  ),
  _DiscoverEntry(context.l10n.services, AppIllustrations.services, '/services'),
  _DiscoverEntry(context.l10n.rentals, AppIllustrations.rental, '/rentals'),
  _DiscoverEntry(
    context.l10n.marketplace,
    AppIllustrations.marketplace,
    '/stores',
  ),
  _DiscoverEntry(context.l10n.social, AppIllustrations.social, '/social'),
  _DiscoverEntry(context.l10n.search, Icons.manage_search_rounded, '/search'),
];

class _DiscoverEntry {
  const _DiscoverEntry(this.label, this.icon, this.route);

  final String label;
  final IconData icon;
  final String route;
}
