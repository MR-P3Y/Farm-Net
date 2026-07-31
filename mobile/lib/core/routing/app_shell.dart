import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../localization/app_localizations.dart';
import '../responsive/responsive.dart';
import '../theme/app_icons.dart';
import '../theme/app_radius.dart';
import '../theme/app_theme_extensions.dart';

class FarmAppShell extends StatelessWidget {
  const FarmAppShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  void _select(int index) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    if (width >= AppBreakpoints.tablet) {
      return _DesktopShell(
        navigationShell: navigationShell,
        onSelect: _select,
        extended: width >= AppBreakpoints.desktop,
      );
    }

    return Scaffold(
      extendBody: true,
      body: navigationShell,
      bottomNavigationBar: _GlassBottomNavigation(
        currentIndex: navigationShell.currentIndex,
        onSelect: _select,
      ),
    );
  }
}

class _DesktopShell extends StatelessWidget {
  const _DesktopShell({
    required this.navigationShell,
    required this.onSelect,
    required this.extended,
  });

  final StatefulNavigationShell navigationShell;
  final ValueChanged<int> onSelect;
  final bool extended;

  @override
  Widget build(BuildContext context) {
    final destinations = _destinations(context);
    return Scaffold(
      body: Row(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(AppRadius.lg),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                  child: NavigationRail(
                    extended: extended,
                    selectedIndex: navigationShell.currentIndex,
                    onDestinationSelected: onSelect,
                    backgroundColor: context.glassTheme.surfaceStrong,
                    leading: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      child: Icon(
                        AppIcons.barzegar,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    destinations: [
                      for (final destination in destinations)
                        NavigationRailDestination(
                          icon: Icon(destination.icon),
                          selectedIcon: Icon(destination.selectedIcon),
                          label: Text(destination.label),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          Expanded(child: navigationShell),
        ],
      ),
    );
  }
}

class _GlassBottomNavigation extends StatelessWidget {
  const _GlassBottomNavigation({
    required this.currentIndex,
    required this.onSelect,
  });

  final int currentIndex;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    final destinations = _destinations(context);
    final glass = context.glassTheme;
    return SafeArea(
      top: false,
      minimum: const EdgeInsets.fromLTRB(12, 0, 12, 10),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(AppRadius.xl),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: glass.blur, sigmaY: glass.blur),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: glass.surfaceStrong,
              borderRadius: BorderRadius.circular(AppRadius.xl),
              border: Border.all(color: glass.border),
              boxShadow: [
                BoxShadow(
                  color: glass.shadow,
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: NavigationBar(
              selectedIndex: currentIndex,
              onDestinationSelected: onSelect,
              backgroundColor: Colors.transparent,
              elevation: 0,
              height: 72,
              destinations: [
                for (var index = 0; index < destinations.length; index++)
                  NavigationDestination(
                    icon: _NavigationIcon(
                      icon: destinations[index].icon,
                      highlighted: index == 2,
                    ),
                    selectedIcon: _NavigationIcon(
                      icon: destinations[index].selectedIcon,
                      highlighted: index == 2,
                      selected: true,
                    ),
                    label: destinations[index].label,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NavigationIcon extends StatelessWidget {
  const _NavigationIcon({
    required this.icon,
    required this.highlighted,
    this.selected = false,
  });

  final IconData icon;
  final bool highlighted;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    if (!highlighted) return Icon(icon);
    final colors = Theme.of(context).colorScheme;
    return Container(
      width: 42,
      height: 42,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(colors: [colors.primary, colors.secondary]),
        boxShadow: [
          BoxShadow(
            color: colors.primary.withValues(alpha: selected ? 0.36 : 0.2),
            blurRadius: 14,
          ),
        ],
      ),
      child: Icon(icon, color: colors.onPrimary, size: 22),
    );
  }
}

List<_ShellDestination> _destinations(BuildContext context) => [
  _ShellDestination(
    label: context.l10n.home,
    icon: AppIcons.home,
    selectedIcon: Icons.home_filled,
  ),
  _ShellDestination(
    label: context.l10n.discover,
    icon: AppIcons.discover,
    selectedIcon: Icons.explore,
  ),
  _ShellDestination(
    label: context.l10n.barzegar,
    icon: AppIcons.barzegar,
    selectedIcon: AppIcons.barzegar,
  ),
  _ShellDestination(
    label: context.l10n.myActivity,
    icon: AppIcons.activity,
    selectedIcon: Icons.dashboard_customize,
  ),
  _ShellDestination(
    label: context.l10n.profile,
    icon: AppIcons.profile,
    selectedIcon: Icons.person,
  ),
];

class _ShellDestination {
  const _ShellDestination({
    required this.label,
    required this.icon,
    required this.selectedIcon,
  });

  final String label;
  final IconData icon;
  final IconData selectedIcon;
}
