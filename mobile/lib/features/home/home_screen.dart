import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_localizations.dart';
import '../../core/responsive/responsive.dart';
import '../../core/widgets/farm_app_bar.dart';
import '../auth/state/auth_controller.dart';
import '../notifications/presentation/notification_badge_button.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final user = ref.watch(authControllerProvider).user;

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.appName,
        showBack: false,
        actions: [
          NotificationBadgeButton(
            onPressed: () => context.push('/notifications'),
          ),
        ],
      ),
      body: ResponsiveBuilder(
        builder:
            (context, constraints, r) => SingleChildScrollView(
              padding: r.pagePadding(),
              child: Center(
                child: ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        l10n.welcome,
                        style: Theme.of(context).textTheme.headlineSmall,
                        textAlign: TextAlign.center,
                      ),
                      if (user != null &&
                          (user.email ?? user.phone) != null) ...[
                        SizedBox(height: r.v(6)),
                        Text(
                          user.email ?? user.phone!,
                          textAlign: TextAlign.center,
                        ),
                      ],
                      SizedBox(height: r.v(22)),
                      FilledButton.icon(
                        onPressed: () => context.push('/activity'),
                        icon: const Icon(Icons.dashboard_customize_outlined),
                        label: const Text('مرکز فعالیت‌های من'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () => context.push('/search'),
                        icon: const Icon(Icons.manage_search),
                        label: const Text('جستجو در همه بخش‌ها'),
                      ),
                      SizedBox(height: r.v(24)),
                      Text(
                        'کاوش در فارم‌نت',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      SizedBox(height: r.v(12)),
                      LayoutBuilder(
                        builder: (context, box) {
                          final columns = box.maxWidth >= 720 ? 3 : 2;
                          const actions = [
                            _HomeDestination(
                              title: 'فروشگاه‌ها',
                              route: '/stores',
                              icon: Icons.storefront_outlined,
                            ),
                            _HomeDestination(
                              title: 'محصولات',
                              route: '/products',
                              icon: Icons.inventory_2_outlined,
                            ),
                            _HomeDestination(
                              title: 'خدمات کشاورزی',
                              route: '/services',
                              icon: Icons.home_repair_service_outlined,
                            ),
                            _HomeDestination(
                              title: 'اجاره تجهیزات',
                              route: '/rentals',
                              icon: Icons.agriculture_outlined,
                            ),
                            _HomeDestination(
                              title: 'مشاوران',
                              route: '/consultants',
                              icon: Icons.support_agent_outlined,
                            ),
                            _HomeDestination(
                              title: 'جامعه کشاورزی',
                              route: '/social',
                              icon: Icons.groups_2_outlined,
                            ),
                            _HomeDestination(
                              title: 'آب‌وهوا',
                              route: '/weather',
                              icon: Icons.wb_sunny_outlined,
                            ),
                            _HomeDestination(
                              title: 'مزرعه‌های من',
                              route: '/farms',
                              icon: Icons.grass_outlined,
                            ),
                            _HomeDestination(
                              title: 'سبد خرید',
                              route: '/cart',
                              icon: Icons.shopping_cart_outlined,
                            ),
                          ];
                          return GridView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: actions.length,
                            gridDelegate:
                                SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: columns,
                                  crossAxisSpacing: r.s(12),
                                  mainAxisSpacing: r.s(12),
                                  childAspectRatio: columns == 3 ? 1.9 : 1.5,
                                ),
                            itemBuilder: (context, index) {
                              final action = actions[index];
                              return Card(
                                clipBehavior: Clip.antiAlias,
                                child: InkWell(
                                  onTap: () => context.push(action.route),
                                  child: Padding(
                                    padding: const EdgeInsets.all(12),
                                    child: Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        Icon(action.icon, size: 30),
                                        const SizedBox(height: 8),
                                        Text(
                                          action.title,
                                          textAlign: TextAlign.center,
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          );
                        },
                      ),
                      SizedBox(height: r.v(24)),
                      OutlinedButton.icon(
                        onPressed: () {
                          ref.read(authControllerProvider.notifier).logout();
                        },
                        icon: const Icon(Icons.logout),
                        label: const Text('خروج از حساب'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
      ),
    );
  }
}

class _HomeDestination {
  const _HomeDestination({
    required this.title,
    required this.route,
    required this.icon,
  });

  final String title;
  final String route;
  final IconData icon;
}
