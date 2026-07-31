import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_localizations.dart';
import '../../core/responsive/responsive.dart';
import '../../core/widgets/farm_circular_glass_button.dart';
import '../../core/widgets/farm_glass_card.dart';
import '../auth/state/auth_controller.dart';
import '../notifications/presentation/notification_badge_button.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final user = ref.watch(authControllerProvider).user;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final r = R(
      context,
      BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width,
        maxHeight: MediaQuery.of(context).size.height,
      ),
    );

    return Scaffold(
      key: _scaffoldKey,
      extendBody: true,
      drawer: _HomeDrawer(user: user, l10n: l10n),
      body: Stack(
        children: [
          // ۱. پس‌زمینه پویا و ارگانیک
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors:
                      isDark
                          ? [const Color(0xFF0A1F0C), const Color(0xFF101810)]
                          : [const Color(0xFFF1F8E9), Colors.white],
                ),
              ),
            ),
          ),

          _AnimatedOrb(
            top: -80,
            right: -80,
            color: const Color(
              0xFF2E7D32,
            ).withValues(alpha: isDark ? 0.12 : 0.06),
          ),
          _AnimatedOrb(
            bottom: 120,
            left: -60,
            color: const Color(
              0xFFFFA000,
            ).withValues(alpha: isDark ? 0.08 : 0.04),
          ),

          // ۲. محتوای داشبورد
          SafeArea(
            child: CustomScrollView(
              physics: const BouncingScrollPhysics(),
              slivers: [
                // هدر اختصاصی
                SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: r.s(20),
                      vertical: r.v(12),
                    ),
                    child: Row(
                      children: [
                        FarmCircularGlassButton(
                          icon: Icons.notes_rounded,
                          onTap: () => _scaffoldKey.currentState?.openDrawer(),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _getGreeting(l10n),
                                style: TextStyle(
                                  color:
                                      isDark ? Colors.white70 : Colors.black54,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                user?.email ??
                                    user?.phone ??
                                    l10n.tr(
                                      fa: 'کشاورز پیشرو',
                                      en: 'Progressive farmer',
                                    ),
                                style: TextStyle(
                                  color:
                                      isDark
                                          ? Colors.white
                                          : const Color(0xFF1B5E20),
                                  fontSize: 18,
                                  fontWeight: FontWeight.w900,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        NotificationBadgeButton(
                          onPressed: () => context.push('/notifications'),
                        ),
                      ],
                    ),
                  ),
                ),

                // ویجت هوشمند آب‌وهوا (قابل کلیک)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.fromLTRB(r.s(16), r.v(16), r.s(16), 0),
                    child: InkWell(
                      onTap: () => context.push('/weather'),
                      borderRadius: BorderRadius.circular(32),
                      child: _WeatherHeroWidget(isDark: isDark),
                    ),
                  ),
                ),

                // هاب خدمات اصلی (گرید شیشه‌ای)
                SliverToBoxAdapter(
                  child: _buildSectionHeader(
                    l10n.tr(fa: 'مدیریت و نظارت مزرعه', en: 'Farm management'),
                    isDark,
                  ),
                ),
                SliverPadding(
                  padding: EdgeInsets.symmetric(horizontal: r.s(16)),
                  sliver: SliverGrid(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          mainAxisSpacing: 12,
                          crossAxisSpacing: 12,
                          childAspectRatio: 1.4,
                        ),
                    delegate: SliverChildListDelegate([
                      _DashboardTile(
                        title: l10n.barzegar,
                        subtitle: l10n.tr(
                          fa: 'دستیار هوشمند کشاورز',
                          en: 'Your farming assistant',
                        ),
                        icon: Icons.auto_awesome_rounded,
                        color: Colors.amber.shade800,
                        onTap: () => context.go('/barzegar'),
                      ),
                      _DashboardTile(
                        title: l10n.farms,
                        subtitle: l10n.tr(
                          fa: 'نظارت بر قطعات',
                          en: 'Monitor your plots',
                        ),
                        icon: Icons.grass_rounded,
                        color: Colors.green,
                        onTap: () => context.push('/farms'),
                      ),
                      _DashboardTile(
                        title: l10n.consultants,
                        subtitle: l10n.tr(
                          fa: 'پرسش و پاسخ',
                          en: 'Expert advice',
                        ),
                        icon: Icons.psychology_rounded,
                        color: Colors.purple,
                        onTap: () => context.push('/consultants'),
                      ),
                    ]),
                  ),
                ),

                // بازار و محصولات
                SliverToBoxAdapter(
                  child: _buildSectionHeader(
                    l10n.tr(fa: 'بازار فارم‌نت', en: 'Farm Net marketplace'),
                    isDark,
                  ),
                ),
                SliverToBoxAdapter(
                  child: SizedBox(
                    height: 125,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      padding: EdgeInsets.symmetric(horizontal: r.s(16)),
                      physics: const BouncingScrollPhysics(),
                      children: [
                        _MarketHubItem(
                          title: l10n.tr(fa: 'فروشگاه‌ها', en: 'Stores'),
                          icon: Icons.storefront_rounded,
                          color: Colors.blue,
                          onTap: () => context.push('/stores'),
                        ),
                        _MarketHubItem(
                          title: l10n.tr(fa: 'محصولات', en: 'Products'),
                          icon: Icons.inventory_2_rounded,
                          color: Colors.teal,
                          onTap: () => context.push('/products'),
                        ),
                        _MarketHubItem(
                          title: l10n.services,
                          icon: Icons.handyman_rounded,
                          color: Colors.orange,
                          onTap: () => context.push('/services'),
                        ),
                        _MarketHubItem(
                          title: l10n.rentals,
                          icon: Icons.agriculture_rounded,
                          color: Colors.brown,
                          onTap: () => context.push('/rentals'),
                        ),
                      ],
                    ),
                  ),
                ),

                // نبض جامعه
                SliverToBoxAdapter(
                  child: _buildSectionHeader(
                    l10n.tr(fa: 'نبض جامعه کشاورزان', en: 'Farmer community'),
                    isDark,
                  ),
                ),
                SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: r.s(16)),
                    child: InkWell(
                      onTap: () => context.push('/social'),
                      borderRadius: BorderRadius.circular(28),
                      child: _SocialPulseWidget(isDark: isDark),
                    ),
                  ),
                ),

                const SliverToBoxAdapter(child: SizedBox(height: 130)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, bool isDark) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 28, 24, 12),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w900,
          color: isDark ? Colors.white : const Color(0xFF1B5E20),
        ),
      ),
    );
  }

  String _getGreeting(AppLocalizations l10n) {
    final hour = DateTime.now().hour;
    if (hour < 12) return l10n.tr(fa: 'صبح بخیر؛', en: 'Good morning,');
    if (hour < 17) return l10n.tr(fa: 'ظهر بخیر؛', en: 'Good afternoon,');
    return l10n.tr(fa: 'شب خوش؛', en: 'Good evening,');
  }
}

class _DashboardTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _DashboardTile({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: FarmGlassCard(
        borderRadius: 24,
        blur: 10,
        opacity: isDark ? 0.08 : 0.5,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 28),
            const Spacer(),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14),
            ),
            Text(
              subtitle,
              style: const TextStyle(color: Colors.black45, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}

class _MarketHubItem extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _MarketHubItem({
    required this.title,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      width: 95,
      margin: const EdgeInsets.only(left: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(24),
        child: FarmGlassCard(
          borderRadius: 24,
          blur: 8,
          opacity: isDark ? 0.06 : 0.4,
          padding: EdgeInsets.zero,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _WeatherHeroWidget extends StatelessWidget {
  final bool isDark;
  const _WeatherHeroWidget({required this.isDark});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return FarmGlassCard(
      borderRadius: 32,
      blur: 20,
      opacity: isDark ? 0.1 : 0.65,
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.tr(fa: 'ورامین، تهران', en: 'Varamin, Tehran'),
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2E7D32).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      l10n.tr(
                        fa: 'مناسب برای کوددهی',
                        en: 'Suitable for fertilizing',
                      ),
                      style: const TextStyle(
                        color: Color(0xFF2E7D32),
                        fontWeight: FontWeight.w900,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
              const Column(
                children: [
                  Icon(
                    Icons.wb_cloudy_rounded,
                    color: Colors.blueAccent,
                    size: 42,
                  ),
                  Text(
                    '۲۸°',
                    style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20),
                  ),
                ],
              ),
            ],
          ),
          const Divider(height: 32, color: Colors.black12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _Stat(
                label: l10n.tr(fa: 'رطوبت', en: 'Humidity'),
                value: l10n.tr(fa: '۴۵٪', en: '45%'),
                icon: Icons.water_drop_rounded,
              ),
              _Stat(
                label: l10n.tr(fa: 'باد', en: 'Wind'),
                value: l10n.tr(fa: '۱۸km', en: '18km'),
                icon: Icons.air_rounded,
              ),
              _Stat(
                label: l10n.tr(fa: 'بارش', en: 'Rain'),
                value: l10n.tr(fa: '۵٪', en: '5%'),
                icon: Icons.umbrella_rounded,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SocialPulseWidget extends StatelessWidget {
  final bool isDark;
  const _SocialPulseWidget({required this.isDark});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return FarmGlassCard(
      borderRadius: 28,
      blur: 10,
      opacity: isDark ? 0.08 : 0.45,
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Row(
            children: [
              const CircleAvatar(radius: 18, backgroundColor: Colors.orange),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.tr(
                        fa: 'مهندس علوی (مشاور)',
                        en: 'Engineer Alavi (Consultant)',
                      ),
                      style: const TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 14,
                      ),
                    ),
                    Text(
                      l10n.tr(
                        fa: 'پاسخ به سوال "آبیاری ذرت"',
                        en: 'Answer to "Corn irrigation"',
                      ),
                      style: TextStyle(
                        fontSize: 11,
                        color: isDark ? Colors.white54 : Colors.black45,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.chevron_left_rounded,
                size: 20,
                color: Colors.black26,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            l10n.tr(
              fa:
                  'در این فصل بهتر است آبیاری را در ساعات پایانی شب انجام دهید تا میزان تبخیر سطحی به حداقل برسد و ریشه گیاه فرصت جذب کافی داشته باشد...',
              en:
                  'This season, irrigate late at night to reduce surface evaporation and give roots enough time to absorb water...',
            ),
            style: TextStyle(
              fontSize: 13,
              height: 1.5,
              color: isDark ? Colors.white70 : Colors.black87,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  const _Stat({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 20, color: Colors.blueGrey),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15),
        ),
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }
}

class _AnimatedOrb extends StatelessWidget {
  final double? top, right, bottom, left;
  final Color color;
  const _AnimatedOrb({
    this.top,
    this.right,
    this.bottom,
    this.left,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: top,
      right: right,
      bottom: bottom,
      left: left,
      child: Container(
        width: 280,
        height: 280,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      ),
    );
  }
}

class _HomeDrawer extends StatelessWidget {
  final dynamic user;
  final AppLocalizations l10n;
  const _HomeDrawer({required this.user, required this.l10n});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Drawer(
      child: Container(
        color: isDark ? const Color(0xFF101810) : Colors.white,
        child: Column(
          children: [
            UserAccountsDrawerHeader(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
                ),
              ),
              currentAccountPicture: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: const CircleAvatar(
                  backgroundColor: Colors.white24,
                  child: Icon(Icons.person, size: 40, color: Colors.white),
                ),
              ),
              accountName: Text(
                user?.email?.split('@').first ??
                    l10n.tr(fa: 'کشاورز', en: 'Farmer'),
                style: const TextStyle(fontWeight: FontWeight.w900),
              ),
              accountEmail: Text(
                user?.phone ?? user?.email ?? '',
                style: const TextStyle(color: Colors.white70),
              ),
            ),
            _DrawerItem(
              icon: Icons.account_balance_wallet_rounded,
              label: l10n.tr(fa: 'کیف پول و موجودی', en: 'Wallet and balance'),
              onTap: () => context.push('/finance'),
            ),
            _DrawerItem(
              icon: Icons.workspace_premium_rounded,
              label: l10n.tr(fa: 'ارتقا به حساب ویژه', en: 'Upgrade plan'),
              color: Colors.amber[800],
              onTap: () => context.push('/subscription'),
            ),
            _DrawerItem(
              icon: Icons.history_rounded,
              label: l10n.myActivity,
              onTap: () => context.go('/activity'),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Divider(),
            ),
            _DrawerItem(
              icon: Icons.settings_outlined,
              label: l10n.settings,
              onTap: () => context.go('/profile'),
            ),
            _DrawerItem(
              icon: Icons.help_outline_rounded,
              label: l10n.tr(fa: 'مرکز پشتیبانی', en: 'Help center'),
              onTap: () {},
            ),
            const Spacer(),
            const Divider(),
            _DrawerItem(
              icon: Icons.logout_rounded,
              label: l10n.logout,
              color: Colors.redAccent,
              onTap: () {},
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}

class _DrawerItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color? color;
  final VoidCallback onTap;
  const _DrawerItem({
    required this.icon,
    required this.label,
    this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(
        label,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 14,
        ),
      ),
      onTap: onTap,
    );
  }
}
