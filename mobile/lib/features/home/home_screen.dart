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
  int _bottomNavIndex = 0;

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
                                _getGreeting(),
                                style: TextStyle(
                                  color:
                                      isDark ? Colors.white70 : Colors.black54,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Text(
                                user?.email ?? user?.phone ?? 'کشاورز پیشرو',
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
                  child: _buildSectionHeader('مدیریت و نظارت مزرعه', isDark),
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
                        title: 'مزارع من',
                        subtitle: 'نظارت بر قطعات',
                        icon: Icons.grass_rounded,
                        color: Colors.green,
                        onTap: () => context.push('/farms'),
                      ),
                      _DashboardTile(
                        title: 'مشاوران',
                        subtitle: 'پرسش و پاسخ',
                        icon: Icons.psychology_rounded,
                        color: Colors.purple,
                        onTap: () => context.push('/consultants'),
                      ),
                    ]),
                  ),
                ),

                // بازار و محصولات
                SliverToBoxAdapter(
                  child: _buildSectionHeader('بازار فارم‌نت', isDark),
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
                          title: 'فروشگاه‌ها',
                          icon: Icons.storefront_rounded,
                          color: Colors.blue,
                          onTap: () => context.push('/stores'),
                        ),
                        _MarketHubItem(
                          title: 'محصولات',
                          icon: Icons.inventory_2_rounded,
                          color: Colors.teal,
                          onTap: () => context.push('/products'),
                        ),
                        _MarketHubItem(
                          title: 'خدمات فنی',
                          icon: Icons.handyman_rounded,
                          color: Colors.orange,
                          onTap: () => context.push('/services'),
                        ),
                        _MarketHubItem(
                          title: 'اجاره ماشین',
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
                  child: _buildSectionHeader('نبض جامعه کشاورزان', isDark),
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

          // ۳. نوار ناوبری کریستالی چندمنظوره
          _ProfessionalGlassNav(
            currentIndex: _bottomNavIndex,
            isDark: isDark,
            onTap: (index) => setState(() => _bottomNavIndex = index),
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

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'صبح بخیر؛';
    if (hour < 17) return 'ظهر بخیر؛';
    return 'شب خوش؛';
  }
}

class _ProfessionalGlassNav extends StatelessWidget {
  final int currentIndex;
  final bool isDark;
  final Function(int) onTap;

  const _ProfessionalGlassNav({
    required this.currentIndex,
    required this.isDark,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: 24,
      left: 16,
      right: 16,
      child: FarmGlassCard(
        borderRadius: 35,
        blur: 25,
        opacity: isDark ? 0.12 : 0.75,
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _NavButton(
              icon: Icons.home_rounded,
              label: 'خانه',
              isActive: currentIndex == 0,
              onTap: () => onTap(0),
            ),
            _NavButton(
              icon: Icons.storefront_rounded,
              label: 'فروشگاه',
              isActive: currentIndex == 1,
              onTap: () {
                onTap(1);
                context.push('/stores');
              },
            ),
            _NavButton(
              icon: Icons.agriculture_rounded,
              label: 'اجاره',
              isActive: currentIndex == 2,
              onTap: () {
                onTap(2);
                context.push('/rentals');
              },
            ),
            _NavButton(
              icon: Icons.handyman_rounded,
              label: 'خدمات',
              isActive: currentIndex == 3,
              onTap: () {
                onTap(3);
                context.push('/services');
              },
            ),
            _NavButton(
              icon: Icons.wb_cloudy_rounded,
              label: 'هوا',
              isActive: currentIndex == 4,
              onTap: () {
                onTap(4);
                context.push('/weather');
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _NavButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;
  const _NavButton({
    required this.icon,
    required this.label,
    this.isActive = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final activeColor = const Color(0xFF2E7D32);
    final color = isActive ? activeColor : Colors.grey.withValues(alpha: 0.8);
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: isActive ? FontWeight.w900 : FontWeight.w500,
            ),
          ),
        ],
      ),
    );
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
                  const Text(
                    'ورامین، تهران',
                    style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
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
                    child: const Text(
                      'مناسب برای کوددهی',
                      style: TextStyle(
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
                label: 'رطوبت',
                value: '۴۵٪',
                icon: Icons.water_drop_rounded,
              ),
              _Stat(label: 'باد', value: '۱۸km', icon: Icons.air_rounded),
              _Stat(label: 'بارش', value: '۵٪', icon: Icons.umbrella_rounded),
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
                    const Text(
                      'مهندس علوی (مشاور)',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 14,
                      ),
                    ),
                    Text(
                      'پاسخ به سوال "آبیاری ذرت"',
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
            'در این فصل بهتر است آبیاری را در ساعات پایانی شب انجام دهید تا میزان تبخیر سطحی به حداقل برسد و ریشه گیاه فرصت جذب کافی داشته باشد...',
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
                user?.email?.split('@').first ?? 'کشاورز',
                style: const TextStyle(fontWeight: FontWeight.w900),
              ),
              accountEmail: Text(
                user?.phone ?? user?.email ?? '',
                style: const TextStyle(color: Colors.white70),
              ),
            ),
            _DrawerItem(
              icon: Icons.account_balance_wallet_rounded,
              label: 'کیف پول و موجودی',
              onTap: () => context.push('/finance'),
            ),
            _DrawerItem(
              icon: Icons.workspace_premium_rounded,
              label: 'ارتقا به حساب ویژه',
              color: Colors.amber[800],
              onTap: () => context.push('/subscription'),
            ),
            _DrawerItem(
              icon: Icons.history_rounded,
              label: 'تاریخچه فعالیت‌ها',
              onTap: () => context.push('/activity'),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Divider(),
            ),
            _DrawerItem(
              icon: Icons.settings_outlined,
              label: 'تنظیمات اپلیکیشن',
              onTap: () => context.push('/profile'),
            ),
            _DrawerItem(
              icon: Icons.help_outline_rounded,
              label: 'مرکز پشتیبانی',
              onTap: () {},
            ),
            const Spacer(),
            const Divider(),
            _DrawerItem(
              icon: Icons.logout_rounded,
              label: 'خروج از حساب',
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
