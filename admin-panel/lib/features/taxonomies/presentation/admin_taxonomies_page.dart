import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/auth/admin_auth_state.dart';

class AdminTaxonomyDestination {
  const AdminTaxonomyDestination({
    required this.title,
    required this.description,
    required this.permission,
    required this.location,
    required this.icon,
  });
  final String title;
  final String description;
  final String permission;
  final String location;
  final IconData icon;
}

const adminTaxonomyDestinations = [
  AdminTaxonomyDestination(
    title: 'دسته‌های محصولات',
    description: 'ساختار والد/فرزند، ترتیب، وضعیت و میزان استفاده محصولات',
    permission: 'product_categories.admin_read',
    location: '/product-categories',
    icon: Icons.inventory_2_outlined,
  ),
  AdminTaxonomyDestination(
    title: 'دسته‌های خدمات',
    description: 'ساختار خدمات، ارائه‌دهندگان، پیشنهادها و درخواست‌ها',
    permission: 'service_categories.admin_read',
    location: '/services',
    icon: Icons.agriculture_outlined,
  ),
  AdminTaxonomyDestination(
    title: 'تخصص‌های مشاوران',
    description: 'تخصص‌ها، پروفایل‌های متصل و درخواست‌های مشاوره',
    permission: 'consult_specialties.read',
    location: '/consultant-specialties',
    icon: Icons.support_agent_outlined,
  ),
  AdminTaxonomyDestination(
    title: 'دسته‌های جامعه',
    description: 'موضوعات گفتگو، ترتیب نمایش و تعداد پست‌ها',
    permission: 'social_categories.admin_read',
    location: '/social-categories',
    icon: Icons.forum_outlined,
  ),
];

class AdminTaxonomiesPage extends ConsumerWidget {
  const AdminTaxonomiesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(adminAuthStateProvider);
    final available =
        adminTaxonomyDestinations
            .where((item) => auth.hasPermission(item.permission))
            .toList();
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'مدیریت دسته‌بندی‌ها',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          const Text(
            'هر بخش قوانین مستقل خود را دارد؛ از این صفحه به ابزار مدیریتی همان دامنه وارد شوید.',
          ),
          const SizedBox(height: 20),
          if (available.isEmpty)
            const Expanded(
              child: Center(
                child: Text('برای مدیریت دسته‌بندی‌ها دسترسی ندارید.'),
              ),
            )
          else
            Expanded(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final columns = constraints.maxWidth >= 900 ? 2 : 1;
                  return GridView.builder(
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: columns,
                      childAspectRatio: columns == 2 ? 2.7 : 3.2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: available.length,
                    itemBuilder: (context, index) {
                      final item = available[index];
                      return Card(
                        child: InkWell(
                          borderRadius: BorderRadius.circular(12),
                          onTap: () => context.go(item.location),
                          child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: Row(
                              children: [
                                Icon(item.icon, size: 38),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Text(
                                        item.title,
                                        style:
                                            Theme.of(
                                              context,
                                            ).textTheme.titleMedium,
                                      ),
                                      const SizedBox(height: 6),
                                      Text(item.description),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}
