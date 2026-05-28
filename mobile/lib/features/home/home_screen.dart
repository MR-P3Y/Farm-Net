import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_localizations.dart';
import '../../core/responsive/responsive.dart';
import '../../core/utils/dates.dart';
import '../../core/widgets/farm_app_bar.dart';
import '../../core/widgets/farm_price_text.dart';
import '../auth/state/auth_controller.dart';
import '../notifications/presentation/notification_badge_button.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final auth = ref.watch(authControllerProvider);
    final user = auth.user;

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.appName,
        showBack: false,
        actions: [
          NotificationBadgeButton(
            onPressed: () {
              context.push('/notifications');
            },
          ),
        ],
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return SingleChildScrollView(
            child: Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        l10n.welcome,
                        style: Theme.of(context).textTheme.headlineSmall,
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: r.v(24)),
                      const FarmPriceText(amountToman: 250000),
                      SizedBox(height: r.v(12)),
                      Text(
                        formatJalaliDate(DateTime.now()),
                        textAlign: TextAlign.center,
                      ),
                      if (user != null) ...[
                        SizedBox(height: r.v(12)),
                        Text(
                          user.email ?? user.phone ?? '',
                          textAlign: TextAlign.center,
                        ),
                      ],
                      SizedBox(height: r.v(24)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/profile');
                        },
                        icon: const Icon(Icons.person_outline),
                        label: const Text('پروفایل من'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/stores');
                        },
                        icon: const Icon(Icons.storefront_outlined),
                        label: const Text('مشاهده فروشگاه‌ها'),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/my-store');
                        },
                        icon: const Icon(Icons.add_business_outlined),
                        label: const Text('فروشگاه من'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/products');
                        },
                        icon: const Icon(Icons.inventory_2_outlined),
                        label: const Text('مشاهده محصولات'),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/my-products');
                        },
                        icon: const Icon(Icons.add_box_outlined),
                        label: const Text('محصولات من'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/cart');
                        },
                        icon: const Icon(Icons.shopping_cart_outlined),
                        label: const Text('سبد خرید'),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/orders');
                        },
                        icon: const Icon(Icons.receipt_long_outlined),
                        label: const Text('سفارش‌های من'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/weather');
                        },
                        icon: const Icon(Icons.wb_sunny_outlined),
                        label: const Text('آب‌وهوا'),
                      ),
                      SizedBox(height: r.v(12)),
                      FilledButton.icon(
                        onPressed: () {
                          context.push('/social');
                        },
                        icon: const Icon(Icons.groups_2_outlined),
                        label: const Text('جامعه کشاورزی'),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton.icon(
                        onPressed: () {
                          context.push('/notifications');
                        },
                        icon: const Icon(Icons.notifications_none_outlined),
                        label: const Text('اعلان‌ها'),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton(
                        onPressed: () {
                          ref.read(authControllerProvider.notifier).logout();
                        },
                        child: const Text('خروج'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
