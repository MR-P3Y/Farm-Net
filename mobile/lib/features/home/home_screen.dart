import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_localizations.dart';
import '../../core/utils/digits.dart';
import '../../core/widgets/farm_circular_glass_button.dart';
import '../../core/widgets/farm_empty_view.dart';
import '../../core/widgets/farm_error_view.dart';
import '../../core/widgets/farm_glass_card.dart';
import '../../core/widgets/farm_loading_view.dart';
import '../auth/state/auth_controller.dart';
import '../farms/data/farm_models.dart';
import '../weather/data/weather_models.dart';
import '../weather/domain/weather_condition_localizer.dart';
import 'data/home_dashboard_models.dart';
import 'state/home_dashboard_controller.dart';
import 'state/home_dashboard_state.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    Future.microtask(ref.read(homeDashboardControllerProvider.notifier).load);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(homeDashboardControllerProvider);
    final user = ref.watch(authControllerProvider).user;
    final l10n = context.l10n;

    return Scaffold(
      key: _scaffoldKey,
      drawer: _HomeDrawer(
        onNavigate: (path) {
          Navigator.of(context).pop();
          context.push(path);
        },
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 8),
              child: Row(
                children: [
                  FarmCircularGlassButton(
                    icon: Icons.menu_rounded,
                    onTap: () => _scaffoldKey.currentState?.openDrawer(),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _greeting(l10n),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        Text(
                          user?.email ??
                              user?.phone ??
                              l10n.tr(
                                fa: 'کشاورز فارم‌نت',
                                en: 'Farm Net farmer',
                              ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.w800),
                        ),
                      ],
                    ),
                  ),
                  _NotificationButton(
                    count: state.data.unreadNotifications,
                    onTap: () => context.push('/notifications'),
                  ),
                ],
              ),
            ),
            Expanded(child: _body(state)),
          ],
        ),
      ),
    );
  }

  Widget _body(HomeDashboardState state) {
    final l10n = context.l10n;
    if (state.isLoading) {
      return FarmLoadingView(
        message: l10n.tr(
          fa: 'در حال آماده‌سازی خانه شما…',
          en: 'Preparing your home…',
        ),
      );
    }
    if (state.errorMessage != null) {
      return FarmErrorView(
        message: l10n.tr(
          fa: 'اطلاعات صفحهٔ خانه دریافت نشد.',
          en: 'Home information could not be loaded.',
        ),
        onRetry: ref.read(homeDashboardControllerProvider.notifier).load,
      );
    }

    return RefreshIndicator(
      onRefresh: ref.read(homeDashboardControllerProvider.notifier).refresh,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final width =
              constraints.maxWidth > 960 ? 920.0 : constraints.maxWidth;
          return ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 120),
            children: [
              Align(
                child: SizedBox(
                  width: width,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (state.data.hasPartialFailure) _partialFailure(),
                      _farmSelector(state.data.farms, state.selectedFarm),
                      const SizedBox(height: 14),
                      _WeatherCard(weather: state.data.weather),
                      const SizedBox(height: 22),
                      _sectionTitle(
                        l10n.tr(fa: 'دسترسی سریع', en: 'Quick access'),
                      ),
                      const SizedBox(height: 10),
                      _QuickGrid(onOpen: _open),
                      const SizedBox(height: 22),
                      _sectionTitle(
                        l10n.tr(
                          fa: 'برزگر، همراه هوشمند شما',
                          en: 'Barzegar, your smart companion',
                        ),
                      ),
                      const SizedBox(height: 10),
                      _barzegarCard(state.data),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _partialFailure() => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Material(
      color: Theme.of(context).colorScheme.errorContainer,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.info_outline_rounded),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                context.l10n.tr(
                  fa:
                      'بخشی از اطلاعات در دسترس نیست؛ برای تلاش دوباره صفحه را پایین بکشید.',
                  en: 'Some information is unavailable. Pull down to try again.',
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );

  Widget _farmSelector(List<FarmModel> farms, FarmModel? selected) {
    final l10n = context.l10n;
    if (farms.isEmpty) {
      return FarmGlassCard(
        padding: EdgeInsets.zero,
        child: FarmEmptyView(
          title: l10n.tr(fa: 'هنوز مزرعه‌ای ندارید', en: 'No farm yet'),
          message: l10n.tr(
            fa: 'اولین مزرعه را بسازید تا پیشنهادها متناسب با زمین شما شوند.',
            en: 'Create your first farm to receive relevant suggestions.',
          ),
          icon: Icons.grass_rounded,
          actionLabel: l10n.tr(fa: 'ساخت مزرعه', en: 'Create farm'),
          onAction: () => context.push('/farms'),
        ),
      );
    }
    return FarmGlassCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<int>(
          value: selected?.id,
          isExpanded: true,
          icon: const Icon(Icons.expand_more_rounded),
          items:
              farms
                  .map(
                    (farm) => DropdownMenuItem(
                      value: farm.id,
                      child: Row(
                        children: [
                          const Icon(Icons.landscape_rounded),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              farm.name,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (farm.declaredAreaSqm != null)
                            Text(
                              l10n.tr(
                                fa: '${_area(farm.declaredAreaSqm!)} هکتار',
                                en: '${_area(farm.declaredAreaSqm!)} ha',
                              ),
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                        ],
                      ),
                    ),
                  )
                  .toList(),
          onChanged: (id) {
            if (id == null) return;
            final farm = farms.firstWhere((item) => item.id == id);
            ref.read(homeDashboardControllerProvider.notifier).selectFarm(farm);
          },
        ),
      ),
    );
  }

  Widget _barzegarCard(HomeDashboardData data) {
    final l10n = context.l10n;
    final latest = data.latestConversation;
    return InkWell(
      onTap: () => context.go('/barzegar'),
      borderRadius: BorderRadius.circular(24),
      child: FarmGlassCard(
        child: Row(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: const Icon(Icons.auto_awesome_rounded, size: 28),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    latest?.title ??
                        l10n.tr(fa: 'از برزگر بپرسید', en: 'Ask Barzegar'),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    latest == null
                        ? l10n.tr(
                          fa:
                              'برای تصمیم‌های مزرعه، پاسخ متناسب با شرایط خودتان بگیرید.',
                          en: 'Get advice tailored to your farm conditions.',
                        )
                        : l10n.tr(
                          fa: 'ادامهٔ آخرین گفت‌وگو',
                          en: 'Continue your latest conversation',
                        ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, size: 17),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) => Text(
    text,
    style: Theme.of(
      context,
    ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
  );

  void _open(String path) =>
      path.startsWith('/home') ? context.go(path) : context.push(path);

  String _greeting(AppLocalizations l10n) {
    final hour = DateTime.now().hour;
    if (hour < 12) return l10n.tr(fa: 'صبح بخیر', en: 'Good morning');
    if (hour < 18) return l10n.tr(fa: 'روز بخیر', en: 'Good afternoon');
    return l10n.tr(fa: 'شب بخیر', en: 'Good evening');
  }

  String _area(double squareMeters) =>
      (squareMeters / 10000).toStringAsFixed(2);
}

class _WeatherCard extends StatefulWidget {
  const _WeatherCard({required this.weather});
  final HomeWeatherData weather;

  @override
  State<_WeatherCard> createState() => _WeatherCardState();
}

class _WeatherCardState extends State<_WeatherCard> {
  late final PageController _controller;
  Timer? _timer;
  int _index = 0;

  @override
  void initState() {
    super.initState();
    _controller = PageController();
    _schedule();
  }

  @override
  void didUpdateWidget(covariant _WeatherCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    final count = widget.weather.effectiveSources.length;
    if (_index >= count) _index = 0;
    _schedule();
  }

  void _schedule() {
    _timer?.cancel();
    if (widget.weather.effectiveSources.length < 2) return;
    _timer = Timer.periodic(const Duration(seconds: 6), (_) {
      if (!mounted || !_controller.hasClients) return;
      final count = widget.weather.effectiveSources.length;
      final next = (_index + 1) % count;
      _controller.animateToPage(
        next,
        duration: const Duration(milliseconds: 550),
        curve: Curves.easeInOutCubic,
      );
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final sources = widget.weather.effectiveSources;
    if (sources.isEmpty) {
      return const _WeatherSourceCard(weather: HomeWeatherData());
    }
    if (sources.length == 1) {
      return _WeatherSourceCard(weather: _sourceData(sources.single));
    }
    return Column(
      children: [
        SizedBox(
          height: 238,
          child: PageView.builder(
            controller: _controller,
            itemCount: sources.length,
            onPageChanged: (value) => setState(() => _index = value),
            itemBuilder:
                (context, index) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 1),
                  child: _WeatherSourceCard(
                    weather: _sourceData(sources[index]),
                  ),
                ),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            sources.length,
            (index) => GestureDetector(
              onTap:
                  () => _controller.animateToPage(
                    index,
                    duration: const Duration(milliseconds: 350),
                    curve: Curves.easeOut,
                  ),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                width: index == _index ? 22 : 7,
                height: 7,
                margin: const EdgeInsets.symmetric(horizontal: 3),
                decoration: BoxDecoration(
                  color:
                      index == _index
                          ? Theme.of(context).colorScheme.primary
                          : Theme.of(
                            context,
                          ).colorScheme.onSurface.withValues(alpha: 0.22),
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  HomeWeatherData _sourceData(HomeWeatherSource source) => HomeWeatherData(
    location: source.location,
    current: source.current,
    forecasts: source.forecasts,
    alerts: source.alerts,
    farmPlot: source.farmPlot,
    farmWeather: source.farmWeather,
  );
}

class _WeatherSourceCard extends StatelessWidget {
  const _WeatherSourceCard({required this.weather});
  final HomeWeatherData weather;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final farmWeather = weather.farmWeather;
    final farmPlot = weather.farmPlot;
    final location = weather.location;
    final current = weather.current;
    return InkWell(
      onTap: () => context.push('/weather'),
      borderRadius: BorderRadius.circular(24),
      child: FarmGlassCard(
        child:
            farmWeather != null
                ? _farmContext(context, farmPlot!, farmWeather)
                : farmPlot != null &&
                    (farmPlot.latitude == null || farmPlot.longitude == null)
                ? _plotNeedsCoordinates(context, farmPlot)
                : location == null
                ? _missing(context)
                : current == null
                ? _noSnapshot(context, location)
                : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.location_on_outlined, size: 19),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            location.displayName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(l10n.tr(fa: 'هواشناسی', en: 'Weather')),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Icon(
                          _weatherIcon(current.conditionCode),
                          size: 52,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                        const SizedBox(width: 14),
                        Text(
                          '${_number(context, current.temperatureC)}°',
                          style: Theme.of(context).textTheme.displaySmall
                              ?.copyWith(fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            WeatherConditionLocalizer.label(
                              isFa: l10n.isFa,
                              code: current.conditionCode,
                              text: current.conditionText,
                              fallback: l10n.tr(
                                fa: 'وضعیت فعلی',
                                en: 'Current conditions',
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 18,
                      runSpacing: 10,
                      children: [
                        _Metric(
                          icon: Icons.water_drop_outlined,
                          text: l10n.tr(
                            fa:
                                'رطوبت ${_number(context, current.humidityPercent)}٪',
                            en:
                                'Humidity ${_number(context, current.humidityPercent)}%',
                          ),
                        ),
                        _Metric(
                          icon: Icons.air_rounded,
                          text: l10n.tr(
                            fa:
                                'باد ${_number(context, current.windSpeedMps)} متر/ثانیه',
                            en:
                                'Wind ${_number(context, current.windSpeedMps)} m/s',
                          ),
                        ),
                        if (weather.alerts.isNotEmpty)
                          _Metric(
                            icon: Icons.warning_amber_rounded,
                            text: l10n.tr(
                              fa:
                                  '${toPersianDigits(weather.alerts.length)} هشدار فعال',
                              en: '${weather.alerts.length} active alerts',
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
      ),
    );
  }

  Widget _farmContext(
    BuildContext context,
    FarmPlotModel plot,
    FarmWeatherModel value,
  ) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          const Icon(Icons.location_on_outlined, size: 19),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              plot.name,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Text(context.l10n.tr(fa: 'هوای دقیق مزرعه', en: 'Farm weather')),
        ],
      ),
      const SizedBox(height: 16),
      Row(
        children: [
          Icon(
            Icons.wb_sunny_rounded,
            size: 52,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(width: 14),
          Text(
            value.temperatureC == null
                ? '—°'
                : '${_localized(context, value.temperatureC!.toStringAsFixed(1))}°',
            style: Theme.of(
              context,
            ).textTheme.displaySmall?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              WeatherConditionLocalizer.label(
                isFa: context.l10n.isFa,
                code: value.snapshot?['condition_code']?.toString(),
                text: value.conditionText,
                fallback: context.l10n.tr(
                  fa: 'وضعیت فعلی',
                  en: 'Current conditions',
                ),
              ),
            ),
          ),
        ],
      ),
      if (value.alerts.isNotEmpty) ...[
        const SizedBox(height: 12),
        _Metric(
          icon: Icons.warning_amber_rounded,
          text: context.l10n.tr(
            fa: '${toPersianDigits(value.alerts.length)} هشدار فعال',
            en: '${value.alerts.length} active alerts',
          ),
        ),
      ],
    ],
  );

  Widget _plotNeedsCoordinates(BuildContext context, FarmPlotModel plot) => Row(
    children: [
      const Icon(Icons.wrong_location_outlined, size: 36),
      const SizedBox(width: 14),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(plot.name, style: Theme.of(context).textTheme.titleMedium),
            Text(
              context.l10n.tr(
                fa: 'برای هوای دقیق، موقعیت جغرافیایی این قطعه را ثبت کنید.',
                en: 'Add this plot’s coordinates for precise weather.',
              ),
            ),
          ],
        ),
      ),
      const Icon(Icons.arrow_forward_ios_rounded, size: 17),
    ],
  );

  Widget _missing(BuildContext context) => Row(
    children: [
      const Icon(Icons.add_location_alt_outlined, size: 36),
      const SizedBox(width: 14),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              context.l10n.tr(
                fa: 'موقعیت هواشناسی ثبت نشده',
                en: 'No weather location',
              ),
              style: Theme.of(context).textTheme.titleMedium,
            ),
            Text(
              context.l10n.tr(
                fa: 'برای دیدن هوای واقعی، یک موقعیت اضافه کنید.',
                en: 'Add a location to see live weather.',
              ),
            ),
          ],
        ),
      ),
      const Icon(Icons.arrow_forward_ios_rounded, size: 17),
    ],
  );

  Widget _noSnapshot(
    BuildContext context,
    WeatherLocationModel location,
  ) => Row(
    children: [
      const Icon(Icons.cloud_off_outlined, size: 36),
      const SizedBox(width: 14),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              location.displayName,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            Text(
              context.l10n.tr(
                fa:
                    'هنوز داده‌ای دریافت نشده؛ برای تازه‌سازی وارد هواشناسی شوید.',
                en: 'No data yet. Open Weather to refresh.',
              ),
            ),
          ],
        ),
      ),
      const Icon(Icons.arrow_forward_ios_rounded, size: 17),
    ],
  );

  static String _number(BuildContext context, String? value) {
    final number = double.tryParse(value ?? '');
    if (number == null) return '—';
    final result =
        number == number.roundToDouble()
            ? number.toInt().toString()
            : number.toStringAsFixed(1);
    return _localized(context, result);
  }

  static String _localized(BuildContext context, String value) =>
      context.l10n.isFa ? toPersianDigits(value) : value;

  static IconData _weatherIcon(String? code) {
    if (code?.startsWith('2') == true) return Icons.thunderstorm_rounded;
    if (code?.startsWith('3') == true || code?.startsWith('5') == true) {
      return Icons.water_drop_rounded;
    }
    if (code?.startsWith('6') == true) return Icons.ac_unit_rounded;
    if (code?.startsWith('8') == true && code != '800') {
      return Icons.cloud_rounded;
    }
    return Icons.wb_sunny_rounded;
  }
}

class _Metric extends StatelessWidget {
  const _Metric({required this.icon, required this.text});
  final IconData icon;
  final String text;
  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [Icon(icon, size: 18), const SizedBox(width: 5), Text(text)],
  );
}

class _QuickGrid extends StatelessWidget {
  const _QuickGrid({required this.onOpen});
  final ValueChanged<String> onOpen;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final items = [
      (l10n.farms, Icons.grass_rounded, '/farms'),
      (
        l10n.tr(fa: 'هواشناسی', en: 'Weather'),
        Icons.cloud_outlined,
        '/weather',
      ),
      (l10n.consultants, Icons.psychology_outlined, '/consultants'),
      (l10n.services, Icons.handyman_outlined, '/services'),
      (l10n.rentals, Icons.agriculture_outlined, '/rentals'),
      (
        l10n.tr(fa: 'بازار', en: 'Marketplace'),
        Icons.storefront_outlined,
        '/stores',
      ),
    ];
    return LayoutBuilder(
      builder: (context, constraints) {
        final columns = constraints.maxWidth >= 720 ? 6 : 3;
        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: items.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: columns,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: .95,
          ),
          itemBuilder: (context, index) {
            final item = items[index];
            return InkWell(
              onTap: () => onOpen(item.$3),
              borderRadius: BorderRadius.circular(20),
              child: FarmGlassCard(
                padding: const EdgeInsets.all(10),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      item.$2,
                      size: 28,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      item.$1,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}

class _NotificationButton extends StatelessWidget {
  const _NotificationButton({required this.count, required this.onTap});
  final int count;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Stack(
    clipBehavior: Clip.none,
    children: [
      FarmCircularGlassButton(
        icon: Icons.notifications_none_rounded,
        onTap: onTap,
      ),
      if (count > 0)
        Positioned(
          top: -2,
          right: -2,
          child: Container(
            constraints: const BoxConstraints(minWidth: 18, minHeight: 18),
            padding: const EdgeInsets.symmetric(horizontal: 4),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.error,
              borderRadius: BorderRadius.circular(10),
            ),
            alignment: Alignment.center,
            child: Text(
              count > 99 ? '99+' : '$count',
              style: TextStyle(
                fontSize: 10,
                color: Theme.of(context).colorScheme.onError,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
    ],
  );
}

class _HomeDrawer extends StatelessWidget {
  const _HomeDrawer({required this.onNavigate});
  final ValueChanged<String> onNavigate;
  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Drawer(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(12),
          children: [
            ListTile(
              leading: const Icon(Icons.eco_rounded),
              title: Text(
                l10n.appName,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
              ),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.person_outline_rounded),
              title: Text(l10n.profile),
              onTap: () => onNavigate('/profile'),
            ),
            ListTile(
              leading: const Icon(Icons.notifications_outlined),
              title: Text(l10n.tr(fa: 'اعلان‌ها', en: 'Notifications')),
              onTap: () => onNavigate('/notifications'),
            ),
            ListTile(
              leading: const Icon(Icons.settings_outlined),
              title: Text(l10n.settings),
              onTap: () => onNavigate('/settings'),
            ),
          ],
        ),
      ),
    );
  }
}
