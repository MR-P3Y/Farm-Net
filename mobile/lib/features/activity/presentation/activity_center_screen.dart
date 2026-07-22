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

          final personal = ActivityCatalog.forUser(user).firstWhere(
            (section) => section.kind == ActivitySectionKind.personal,
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
                          user.roles.where((role) => role != 'user').length,
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
