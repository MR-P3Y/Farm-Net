import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../localization/admin_localizations.dart';
import '../auth/admin_auth_state.dart';

const adminTaxonomyPermissions = [
  'product_categories.admin_read',
  'service_categories.admin_read',
  'consult_specialties.read',
  'social_categories.admin_read',
];

class AdminSidebar extends ConsumerWidget {
  const AdminSidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AdminLocalizations.of(context);
    final colorScheme = Theme.of(context).colorScheme;
    final canManageTaxonomies = ref
        .watch(adminAuthStateProvider)
        .hasAnyPermission(adminTaxonomyPermissions);
    final canReadReviews = ref.watch(adminAuthStateProvider).hasAnyPermission(
      const ['reviews.admin_read', 'review_reports.admin_read'],
    );
    final canReadFarms = ref
        .watch(adminAuthStateProvider)
        .hasPermission('farms.admin_read');

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
                if (canManageTaxonomies)
                  _SidebarItem(
                    icon: Icons.category_outlined,
                    label: 'مدیریت دسته‌بندی‌ها',
                    compact: isCompact,
                    onTap: () => context.go('/taxonomies'),
                  ),
                _SidebarItem(
                  icon: Icons.receipt_long_outlined,
                  label: 'خدمات کشاورزی',
                  compact: isCompact,
                  onTap: () => context.go('/services'),
                ),
                _SidebarItem(
                  icon: Icons.agriculture_outlined,
                  label: 'اجاره تجهیزات',
                  compact: isCompact,
                  onTap: () => context.go('/rentals'),
                ),
                if (canReadFarms)
                  _SidebarItem(
                    icon: Icons.landscape_outlined,
                    label: 'پشتیبانی مزارع',
                    compact: isCompact,
                    onTap: () => context.go('/farms'),
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
                  icon: Icons.support_agent_outlined,
                  label: 'مشاوران',
                  compact: isCompact,
                  onTap: () => context.go('/consultants'),
                ),
                _SidebarItem(
                  icon: Icons.perm_media_outlined,
                  label: 'فایل‌ها',
                  compact: isCompact,
                  onTap: () => context.go('/media'),
                ),
                _SidebarItem(
                  icon: Icons.notifications_none_outlined,
                  label: 'اعلان‌ها',
                  compact: isCompact,
                  onTap: () => context.go('/notifications'),
                ),
                _SidebarItem(
                  icon: Icons.wb_sunny_outlined,
                  label: 'آب‌وهوا',
                  compact: isCompact,
                  onTap: () => context.go('/weather'),
                ),
                _SidebarItem(
                  icon: Icons.groups_2_outlined,
                  label: 'مدیریت جامعه',
                  compact: isCompact,
                  onTap: () => context.go('/social'),
                ),
                if (canReadReviews)
                  _SidebarItem(
                    icon: Icons.rate_review_outlined,
                    label: 'نظرات و گزارش‌ها',
                    compact: isCompact,
                    onTap: () => context.go('/reviews'),
                  ),
                _SidebarItem(
                  icon: Icons.payments_outlined,
                  label: l10n.finance,
                  compact: isCompact,
                  onTap: () => context.go('/finance'),
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
