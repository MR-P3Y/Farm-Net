import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../auth/state/auth_controller.dart';
import '../data/activity_catalog.dart';

class ActivityCenterScreen extends ConsumerWidget {
  const ActivityCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider);
    final user = auth.user;

    return Scaffold(
      appBar: const FarmAppBar(title: 'مرکز فعالیت‌های من'),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (auth.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (!auth.isAuthenticated || user == null) {
            return _SignedOutView(padding: r.pagePadding());
          }

          final catalog = ActivityCatalog.forUser(user);
          final professionalRoles = ActivityCatalog.professionalRolesForUser(
            user,
          );
          final personal = catalog.firstWhere(
            (section) => section.kind == ActivitySectionKind.personal,
          );
          final businessSections = catalog.where(
            (section) =>
                section.kind == ActivitySectionKind.shop ||
                section.kind == ActivitySectionKind.services ||
                section.kind == ActivitySectionKind.rental ||
                section.kind == ActivitySectionKind.consultant,
          );

          return SingleChildScrollView(
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 880),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _IdentityCard(
                      identity: user.email ?? user.phone ?? 'کاربر فارم‌نت',
                      rolesCount:
                          professionalRoles
                              .where((role) => role.isActive)
                              .length,
                    ),
                    SizedBox(height: r.v(16)),
                    _ProfessionalRolesCard(
                      roles: professionalRoles,
                      onSetup: (role) => context.push(role.setupRoute),
                      onVerifications: () => context.push('/verifications'),
                      onRefresh:
                          () =>
                              ref
                                  .read(authControllerProvider.notifier)
                                  .loadCurrentUser(),
                    ),
                    SizedBox(height: r.v(20)),
                    Text(
                      personal.title,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    SizedBox(height: r.v(12)),
                    LayoutBuilder(
                      builder: (context, box) {
                        final columns = box.maxWidth >= 720 ? 3 : 2;
                        return GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: personal.actions.length,
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: columns,
                                crossAxisSpacing: r.s(12),
                                mainAxisSpacing: r.s(12),
                                childAspectRatio: columns == 3 ? 1.75 : 1.35,
                              ),
                          itemBuilder: (context, index) {
                            final action = personal.actions[index];
                            return _ActivityActionCard(
                              action: action,
                              onTap: () => context.push(action.route),
                            );
                          },
                        );
                      },
                    ),
                    for (final section in businessSections) ...[
                      SizedBox(height: r.v(24)),
                      _BusinessActivitySection(
                        section: section,
                        onAction: (action) => context.push(action.route),
                      ),
                    ],
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

class _ProfessionalRolesCard extends StatelessWidget {
  const _ProfessionalRolesCard({
    required this.roles,
    required this.onSetup,
    required this.onVerifications,
    required this.onRefresh,
  });

  final List<ProfessionalRoleJourney> roles;
  final ValueChanged<ProfessionalRoleJourney> onSetup;
  final VoidCallback onVerifications;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Icon(Icons.workspace_premium_outlined),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'نقش‌های حرفه‌ای من',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
              IconButton(
                tooltip: 'به‌روزرسانی نقش‌ها',
                onPressed: onRefresh,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ...roles.map(
            (role) => ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(
                role.isActive
                    ? Icons.verified_outlined
                    : Icons.pending_actions_outlined,
                color:
                    role.isActive
                        ? Theme.of(context).colorScheme.primary
                        : null,
              ),
              title: Text(role.title),
              subtitle: Text(
                role.isActive ? 'فعال و تأییدشده' : role.setupLabel,
              ),
              onTap: role.isActive ? null : () => onSetup(role),
              trailing:
                  role.isActive
                      ? const Chip(label: Text('فعال'))
                      : const Icon(Icons.chevron_left),
            ),
          ),
          const Divider(),
          TextButton.icon(
            onPressed: onVerifications,
            icon: const Icon(Icons.fact_check_outlined),
            label: const Text('مشاهده همه درخواست‌های تأیید'),
          ),
        ],
      ),
    ),
  );
}

class _BusinessActivitySection extends StatelessWidget {
  const _BusinessActivitySection({
    required this.section,
    required this.onAction,
  });

  final ActivitySection section;
  final ValueChanged<ActivityAction> onAction;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Row(
        children: [
          Icon(_sectionIcon(section.kind)),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              section.title,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          if (section.isSetupSection)
            const Chip(label: Text('نیازمند تکمیل و تأیید')),
        ],
      ),
      const SizedBox(height: 12),
      ...section.actions.map(
        (action) => Card(
          child: ListTile(
            leading: Icon(_actionIcon(action.id)),
            title: Text(action.title),
            trailing: const Icon(Icons.chevron_left),
            onTap: () => onAction(action),
          ),
        ),
      ),
    ],
  );

  IconData _sectionIcon(ActivitySectionKind kind) => switch (kind) {
    ActivitySectionKind.shop => Icons.storefront_outlined,
    ActivitySectionKind.services => Icons.home_repair_service_outlined,
    ActivitySectionKind.rental => Icons.agriculture_outlined,
    ActivitySectionKind.consultant => Icons.support_agent_outlined,
    ActivitySectionKind.personal => Icons.person_outline,
  };

  IconData _actionIcon(ActivityActionId id) => switch (id) {
    ActivityActionId.shopProfile => Icons.store_outlined,
    ActivityActionId.shopProducts => Icons.inventory_2_outlined,
    ActivityActionId.sellerOrders => Icons.receipt_long_outlined,
    ActivityActionId.serviceProviderProfile => Icons.badge_outlined,
    ActivityActionId.serviceOffers => Icons.design_services_outlined,
    ActivityActionId.serviceWorkbench => Icons.work_outline,
    ActivityActionId.lessorProfile => Icons.badge_outlined,
    ActivityActionId.rentalEquipment => Icons.agriculture_outlined,
    ActivityActionId.rentalWorkbench => Icons.work_history_outlined,
    ActivityActionId.consultantProfile => Icons.badge_outlined,
    ActivityActionId.consultantWorkbench => Icons.support_agent_outlined,
    _ => Icons.chevron_left,
  };
}

class _IdentityCard extends StatelessWidget {
  const _IdentityCard({required this.identity, required this.rolesCount});

  final String identity;
  final int rolesCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            const CircleAvatar(radius: 25, child: Icon(Icons.person_outline)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    identity,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 5),
                  Text(
                    rolesCount == 0
                        ? 'فعالیت‌های شخصی'
                        : '$rolesCount نقش حرفه‌ای فعال',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActivityActionCard extends StatelessWidget {
  const _ActivityActionCard({required this.action, required this.onTap});

  final ActivityAction action;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(_iconFor(action.id), size: 30),
              const SizedBox(height: 10),
              Text(
                action.title,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.titleSmall,
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _iconFor(ActivityActionId id) => switch (id) {
    ActivityActionId.profile => Icons.person_outline,
    ActivityActionId.verifications => Icons.verified_user_outlined,
    ActivityActionId.notifications => Icons.notifications_none_outlined,
    ActivityActionId.finance => Icons.account_balance_wallet_outlined,
    ActivityActionId.buyerOrders => Icons.receipt_long_outlined,
    ActivityActionId.serviceRequests => Icons.home_repair_service_outlined,
    ActivityActionId.rentalRequests => Icons.agriculture_outlined,
    ActivityActionId.consultationRequests => Icons.support_agent_outlined,
    ActivityActionId.reviews => Icons.rate_review_outlined,
    _ => Icons.work_outline,
  };
}

class _SignedOutView extends StatelessWidget {
  const _SignedOutView({required this.padding});

  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: padding,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.lock_outline, size: 52),
            const SizedBox(height: 14),
            const Text('برای مشاهده فعالیت‌های خود ابتدا وارد حساب شوید.'),
            const SizedBox(height: 18),
            FilledButton(
              onPressed: () => context.go('/'),
              child: const Text('ورود به حساب'),
            ),
          ],
        ),
      ),
    );
  }
}
