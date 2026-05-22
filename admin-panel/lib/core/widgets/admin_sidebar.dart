import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../localization/admin_localizations.dart';

class AdminSidebar extends StatelessWidget {
  const AdminSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AdminLocalizations.of(context);
    final colorScheme = Theme.of(context).colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 120;

        return Container(
          color: colorScheme.surface,
          child: SafeArea(
            child: Column(
              children: [
                const SizedBox(height: 16),
                if (isCompact)
                  const Icon(Icons.eco_outlined)
                else
                  Text(
                    'Farm Net',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                const Divider(height: 32),
                _SidebarItem(
                  icon: Icons.dashboard_outlined,
                  label: l10n.dashboard,
                  compact: isCompact,
                  onTap: () => context.go('/dashboard'),
                ),
                _SidebarItem(
                  icon: Icons.people_outline,
                  label: l10n.users,
                  compact: isCompact,
                  onTap: () {},
                ),
                _SidebarItem(
                  icon: Icons.storefront_outlined,
                  label: l10n.shops,
                  compact: isCompact,
                  onTap: () => context.go('/stores'),
                ),
                _SidebarItem(
                  icon: Icons.inventory_2_outlined,
                  label: l10n.products,
                  compact: isCompact,
                  onTap: () => context.go('/products'),
                ),
                _SidebarItem(
                  icon: Icons.receipt_long_outlined,
                  label: 'سفارش‌ها',
                  compact: isCompact,
                  onTap: () => context.go('/orders'),
                ),
                _SidebarItem(
                  icon: Icons.percent_outlined,
                  label: 'کمیسیون',
                  compact: isCompact,
                  onTap: () => context.go('/commission'),
                ),
                _SidebarItem(
                  icon: Icons.perm_media_outlined,
                  label: 'فایل‌ها',
                  compact: isCompact,
                  onTap: () => context.go('/media'),
                ),
                _SidebarItem(
                  icon: Icons.payments_outlined,
                  label: l10n.finance,
                  compact: isCompact,
                  onTap: () {},
                ),
                _SidebarItem(
                  icon: Icons.verified_user_outlined,
                  label: 'درخواست‌های تأیید',
                  compact: isCompact,
                  onTap: () => context.go('/verifications'),
                ),
                const Spacer(),
                _SidebarItem(
                  icon: Icons.settings_outlined,
                  label: l10n.settings,
                  compact: isCompact,
                  onTap: () {},
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SidebarItem extends StatelessWidget {
  const _SidebarItem({
    required this.icon,
    required this.label,
    required this.compact,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool compact;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: label,
      child: ListTile(
        leading: Icon(icon),
        title: compact ? null : Text(label, overflow: TextOverflow.ellipsis),
        onTap: onTap,
      ),
    );
  }
}
