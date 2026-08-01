import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_circular_glass_button.dart';
import '../../../core/widgets/farm_error_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../farms/data/farm_models.dart';
import '../../farms/data/farm_repository.dart';
import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/weather_models.dart';
import '../domain/weather_operation_planner.dart';
import '../state/weather_controller.dart';

class WeatherScreen extends ConsumerStatefulWidget {
  const WeatherScreen({super.key});

  @override
  ConsumerState<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends ConsumerState<WeatherScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(() => ref.read(weatherControllerProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(weatherControllerProvider);
    final l10n = context.l10n;
    final observedAt =
        DateTime.tryParse(state.current?.observedAt ?? '')?.toLocal();
    final hourlyForecasts = _next24Hours(state.forecasts);
    final dailyForecasts = _dailyForecasts(state.forecasts);
    final operationPlans = const WeatherOperationPlanner().plan(
      state.forecasts,
    );

    if (state.isLoading && state.locations.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          leading: const FarmBackButton(),
          title: Text(l10n.weather),
        ),
        body: FarmLoadingView(
          message: l10n.tr(
            fa: 'در حال آماده‌سازی پایش آب‌وهوا...',
            en: 'Preparing weather monitoring...',
          ),
        ),
      );
    }

    if (state.errorMessage != null && state.current == null) {
      return Scaffold(
        appBar: AppBar(
          leading: const FarmBackButton(),
          title: Text(l10n.weather),
        ),
        body: FarmErrorView(
          message: l10n.tr(
            fa: state.errorMessage!,
            en: 'Weather data could not be loaded. Please try again.',
          ),
          onRetry: () {
            final controller = ref.read(weatherControllerProvider.notifier);
            if (state.isFarmSource) {
              controller.loadFarmPlot(
                farmId: state.selectedFarmId!,
                plotId: state.selectedPlotId!,
                farmName: state.selectedFarmName ?? '',
                plotName: state.selectedPlotName ?? '',
              );
            } else if (state.selectedLocation != null) {
              controller.loadLocation(state.selectedLocation!);
            } else {
              controller.load();
            }
          },
        ),
      );
    }

    if (state.locations.isEmpty && !state.isFarmSource) {
      return _NoWeatherLocationView(
        onChooseLocation: () => _showLocationPicker(context),
      );
    }
    final isDarkGlobal = Theme.of(context).brightness == Brightness.dark;

    final hour = DateTime.now().hour;
    final isActuallyNight = hour < 6 || hour > 19;

    final atmosphere = _getAtmosphere(
      state.current?.conditionText,
      isActuallyNight || isDarkGlobal,
    );

    return Scaffold(
      body: Stack(
        children: [
          Positioned.fill(
            child: AnimatedContainer(
              duration: const Duration(seconds: 2),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: atmosphere.colors,
                ),
              ),
            ),
          ),

          _PositionedOrb(
            top: 100,
            right: -50,
            color: Colors.white.withValues(alpha: 0.1),
          ),
          _PositionedOrb(
            bottom: -50,
            left: -50,
            color: atmosphere.accentColor.withValues(alpha: 0.2),
          ),

          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1100),
                child: CustomScrollView(
                  physics: const BouncingScrollPhysics(),
                  slivers: [
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const FarmBackButton(),
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                ),
                                child: Column(
                                  children: [
                                    Text(
                                      state.farmDisplayName ??
                                          state.selectedLocation?.displayName ??
                                          l10n.tr(
                                            fa: 'موقعیت نامشخص',
                                            en: 'Unknown location',
                                          ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.w900,
                                        fontSize: 18,
                                        shadows: [
                                          Shadow(
                                            color: Colors.black26,
                                            blurRadius: 10,
                                          ),
                                        ],
                                      ),
                                    ),
                                    Text(
                                      isActuallyNight
                                          ? l10n.tr(
                                            fa: 'پایش شبانه',
                                            en: 'Night monitoring',
                                          )
                                          : l10n.tr(
                                            fa: 'پایش روزانه',
                                            en: 'Day monitoring',
                                          ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: TextStyle(
                                        color: Colors.white.withValues(
                                          alpha: 0.7,
                                        ),
                                        fontSize: 11,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                FarmCircularGlassButton(
                                  icon: Icons.refresh_rounded,
                                  onTap:
                                      state.isSaving
                                          ? null
                                          : () =>
                                              ref
                                                  .read(
                                                    weatherControllerProvider
                                                        .notifier,
                                                  )
                                                  .refreshSelected(),
                                ),
                                const SizedBox(width: 8),
                                FarmCircularGlassButton(
                                  icon: Icons.map_rounded,
                                  onTap: () => _showLocationPicker(context),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),

                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 30),
                        child: Column(
                          children: [
                            _WeatherIcon(
                              condition: state.current?.conditionText,
                              isNight: isActuallyNight,
                            ),
                            const SizedBox(height: 10),
                            Stack(
                              alignment: Alignment.center,
                              children: [
                                Container(
                                  width: 150,
                                  height: 150,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.white.withValues(
                                          alpha: 0.15,
                                        ),
                                        blurRadius: 80,
                                      ),
                                    ],
                                  ),
                                ),
                                Text(
                                  _localizedNumber(
                                    context,
                                    '${double.tryParse(state.current?.temperatureC ?? '')?.round() ?? '--'}°',
                                  ),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 120,
                                    fontWeight: FontWeight.w900,
                                    fontFamily: 'IRYekan',
                                    height: 1,
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              state.errorMessage ??
                                  state.current?.conditionText ??
                                  (state.isSaving
                                      ? l10n.tr(
                                        fa: 'در حال دریافت اطلاعات هواشناسی...',
                                        en: 'Fetching weather data...',
                                      )
                                      : l10n.tr(
                                        fa: 'اطلاعات هواشناسی دریافت نشد',
                                        en: 'Weather data is unavailable',
                                      )),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 24,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 1.2,
                              ),
                            ),
                            if (observedAt != null) ...[
                              const SizedBox(height: 8),
                              Text(
                                l10n.tr(
                                  fa:
                                      'آخرین مشاهده: ${formatDate(context, observedAt, showTime: true)}',
                                  en:
                                      'Last observed: ${formatDate(context, observedAt, showTime: true)}',
                                ),
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: 0.68),
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),

                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        child: FarmGlassCard(
                          borderRadius: 30,
                          opacity: 0.12,
                          blur: 20,
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    Icons.auto_awesome_rounded,
                                    color: Colors.amber[300],
                                    size: 24,
                                  ),
                                  const SizedBox(width: 12),
                                  Text(
                                    l10n.tr(
                                      fa: 'راهنمای کشاورزی امروز',
                                      en: "Today's farming guidance",
                                    ),
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.w900,
                                      fontSize: 15,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _getFarmAdvice(context, state.current),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 13,
                                  height: 1.6,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),

                    if (state.alerts.isNotEmpty)
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                          child: _WeatherAlerts(alerts: state.alerts),
                        ),
                      ),

                    SliverPadding(
                      padding: const EdgeInsets.all(20),
                      sliver: SliverGrid(
                        gridDelegate:
                            const SliverGridDelegateWithFixedCrossAxisCount(
                              crossAxisCount: 3,
                              mainAxisSpacing: 16,
                              crossAxisSpacing: 16,
                              childAspectRatio: 0.85,
                            ),
                        delegate: SliverChildListDelegate([
                          _MetricCard(
                            label: l10n.tr(fa: 'رطوبت', en: 'Humidity'),
                            value: _localizedNumber(
                              context,
                              '${state.current?.humidityPercent ?? '--'}%',
                            ),
                            icon: Icons.water_drop_rounded,
                          ),
                          _MetricCard(
                            label: l10n.tr(fa: 'سرعت باد', en: 'Wind'),
                            value: _localizedNumber(
                              context,
                              '${state.current?.windSpeedMps ?? '--'} m/s',
                            ),
                            icon: Icons.air_rounded,
                          ),
                          _MetricCard(
                            label: l10n.tr(fa: 'فشار', en: 'Pressure'),
                            value: _localizedNumber(
                              context,
                              '${state.current?.pressureHpa ?? '--'} hPa',
                            ),
                            icon: Icons.shutter_speed_rounded,
                          ),
                        ]),
                      ),
                    ),

                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(24, 10, 24, 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              l10n.tr(
                                fa: 'پیش‌بینی ساعتی',
                                en: 'Hourly forecast',
                              ),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            Text(
                              l10n.tr(fa: '۲۴ ساعت آینده', en: 'Next 24 hours'),
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.5),
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: SizedBox(
                        height: 172,
                        child: ListView.builder(
                          scrollDirection: Axis.horizontal,
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          physics: const BouncingScrollPhysics(),
                          itemCount: hourlyForecasts.length,
                          itemBuilder: (context, index) {
                            final forecast = hourlyForecasts[index];
                            return _HourlyForecastItem(
                              forecast: forecast,
                              isNight: isActuallyNight,
                            );
                          },
                        ),
                      ),
                    ),
                    if (dailyForecasts.isNotEmpty) ...[
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(24, 28, 24, 12),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                l10n.tr(
                                  fa: 'پیش‌بینی روزهای آینده',
                                  en: 'Upcoming days',
                                ),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                              Text(
                                l10n.tr(
                                  fa:
                                      'پوشش ${toPersianDigits(dailyForecasts.length.toString())} روز',
                                  en: '${dailyForecasts.length}-day coverage',
                                ),
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: 0.55),
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      SliverToBoxAdapter(
                        child: SizedBox(
                          height: 205,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            itemCount: dailyForecasts.length,
                            separatorBuilder:
                                (context, index) => const SizedBox(width: 12),
                            itemBuilder:
                                (context, index) => _DailyForecastCard(
                                  summary: dailyForecasts[index],
                                ),
                          ),
                        ),
                      ),
                    ],
                    if (operationPlans.isNotEmpty)
                      SliverToBoxAdapter(
                        child: _OperationPlannerSection(plans: operationPlans),
                      ),
                    const SliverToBoxAdapter(child: SizedBox(height: 40)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  _Atmosphere _getAtmosphere(String? condition, bool isDark) {
    final cond = (condition ?? '').toLowerCase();

    if (isDark) {
      return _Atmosphere(
        colors: [
          const Color(0xFF0F2027),
          const Color(0xFF203A43),
          const Color(0xFF2C5364),
        ],
        accentColor: Colors.blueGrey,
      );
    }

    if (cond.contains('rain') || cond.contains('باران')) {
      return _Atmosphere(
        colors: [const Color(0xFF2B5876), const Color(0xFF4E4376)],
        accentColor: Colors.blueAccent,
      );
    }

    if (cond.contains('cloud') || cond.contains('ابری')) {
      return _Atmosphere(
        colors: [const Color(0xFF3E5151), const Color(0xFFDECBA4)],
        accentColor: Colors.orangeAccent,
      );
    }

    return _Atmosphere(
      colors: [const Color(0xFF2193B0), const Color(0xFF6dd5ed)],
      accentColor: Colors.yellowAccent,
    );
  }

  String _getFarmAdvice(BuildContext context, WeatherSnapshotModel? current) {
    final l10n = context.l10n;
    if (current == null) {
      return l10n.tr(
        fa: 'برای دریافت راهنما، ابتدا اطلاعات هوا را دریافت کنید.',
        en: 'Fetch weather data first to receive farming guidance.',
      );
    }
    final wind = double.tryParse(current.windSpeedMps ?? '0') ?? 0;
    if (wind > 5) {
      return l10n.tr(
        fa:
            'سرعت باد برای سم‌پاشی زیاد است. عملیات را به ساعات آرام‌تر موکول کنید و پیش از اقدام شرایط مزرعه را بررسی کنید.',
        en:
            'Wind is too strong for spraying. Postpone the operation to calmer hours and verify field conditions first.',
      );
    }
    return l10n.tr(
      fa:
          'باد فعلی مانع آشکاری برای عملیات سبک مزرعه ایجاد نمی‌کند. پیش از آبیاری یا سم‌پاشی، رطوبت خاک و پیش‌بینی ساعات بعد را نیز بررسی کنید.',
      en:
          'Current wind does not indicate an obvious obstacle to light field work. Also check soil moisture and the next-hours forecast before irrigation or spraying.',
    );
  }

  void _showLocationPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const _LocationPickerSheet(),
    );
  }

  List<WeatherForecastModel> _next24Hours(
    List<WeatherForecastModel> forecasts,
  ) {
    final now = DateTime.now();
    final end = now.add(const Duration(hours: 24));
    final rows =
        forecasts.where((forecast) {
          final time = DateTime.tryParse(forecast.forecastTime)?.toLocal();
          return time != null && !time.isBefore(now) && !time.isAfter(end);
        }).toList();
    return rows.isNotEmpty ? rows : forecasts.take(8).toList();
  }

  List<_DailyForecastSummary> _dailyForecasts(
    List<WeatherForecastModel> forecasts,
  ) {
    final groups = <DateTime, List<WeatherForecastModel>>{};
    for (final forecast in forecasts) {
      final time = DateTime.tryParse(forecast.forecastTime)?.toLocal();
      if (time == null) continue;
      final day = DateTime(time.year, time.month, time.day);
      groups.putIfAbsent(day, () => []).add(forecast);
    }
    return groups.entries
        .map((entry) => _DailyForecastSummary.fromRows(entry.key, entry.value))
        .toList()
      ..sort((a, b) => a.date.compareTo(b.date));
  }
}

class _Atmosphere {
  final List<Color> colors;
  final Color accentColor;
  _Atmosphere({required this.colors, required this.accentColor});
}

class _NoWeatherLocationView extends StatelessWidget {
  const _NoWeatherLocationView({required this.onChooseLocation});

  final VoidCallback onChooseLocation;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        leading: const FarmBackButton(),
        title: Text(context.l10n.weather),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 460),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: FarmGlassCard(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.location_on_outlined,
                    size: 64,
                    color: colors.primary,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    context.l10n.tr(
                      fa: 'هنوز موقعیت هواشناسی ندارید',
                      en: 'No weather location yet',
                    ),
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    context.l10n.tr(
                      fa:
                          'موقعیت فعلی یا یکی از شهرهای ایران را انتخاب کنید تا پایش آب‌وهوا آغاز شود.',
                      en:
                          'Choose your current location or an Iranian city to start weather monitoring.',
                    ),
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colors.onSurfaceVariant,
                      height: 1.6,
                    ),
                  ),
                  const SizedBox(height: 24),
                  FarmButton(
                    label: context.l10n.tr(
                      fa: 'انتخاب موقعیت',
                      en: 'Choose location',
                    ),
                    icon: Icons.add_location_alt_rounded,
                    onPressed: onChooseLocation,
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

String _localizedNumber(BuildContext context, String value) {
  return context.l10n.isFa ? toPersianDigits(value) : value;
}

class _WeatherAlerts extends StatelessWidget {
  const _WeatherAlerts({required this.alerts});

  final List<WeatherAlertModel> alerts;

  @override
  Widget build(BuildContext context) {
    final active = [...alerts]..sort(
      (a, b) => _severityRank(b.severity).compareTo(_severityRank(a.severity)),
    );
    return FarmGlassCard(
      borderRadius: 24,
      opacity: 0.12,
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: Colors.amber),
              const SizedBox(width: 10),
              Text(
                context.l10n.tr(fa: 'هشدارهای فعال', en: 'Active alerts'),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          for (var index = 0; index < active.length; index++) ...[
            _WeatherAlertCard(alert: active[index]),
            if (index != active.length - 1) const SizedBox(height: 10),
          ],
        ],
      ),
    );
  }

  static int _severityRank(String severity) => switch (severity) {
    'critical' => 5,
    'high' => 4,
    'medium' => 3,
    'low' => 2,
    _ => 1,
  };
}

class _WeatherAlertCard extends StatelessWidget {
  const _WeatherAlertCard({required this.alert});

  final WeatherAlertModel alert;

  @override
  Widget build(BuildContext context) {
    final accent = _severityColor(alert.severity);
    final startsAt = DateTime.tryParse(alert.startsAt)?.toLocal();
    final endsAt = DateTime.tryParse(alert.endsAt ?? '')?.toLocal();
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.13),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: accent.withValues(alpha: 0.55)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(_alertIcon(alert.alertType), color: accent, size: 25),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _alertTitle(context, alert),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    if (startsAt != null) ...[
                      const SizedBox(height: 3),
                      Text(
                        endsAt == null
                            ? context.l10n.tr(
                              fa:
                                  'شروع: ${formatDate(context, startsAt, showTime: true)}',
                              en:
                                  'Starts: ${formatDate(context, startsAt, showTime: true)}',
                            )
                            : context.l10n.tr(
                              fa:
                                  '${formatDate(context, startsAt, showTime: true)} تا ${formatDate(context, endsAt, showTime: true)}',
                              en:
                                  '${formatDate(context, startsAt, showTime: true)} to ${formatDate(context, endsAt, showTime: true)}',
                            ),
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.62),
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: 0.22),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: Text(
                  _severityLabel(context, alert.severity),
                  style: TextStyle(
                    color: accent,
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 11),
          Text(
            _alertDescription(context, alert),
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.8),
              height: 1.55,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.task_alt_rounded, color: accent, size: 18),
              const SizedBox(width: 7),
              Expanded(
                child: Text(
                  _alertAction(context, alert.alertType),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                    height: 1.45,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _severityColor(String severity) => switch (severity) {
    'critical' => const Color(0xFFFF5252),
    'high' => const Color(0xFFFF7043),
    'medium' => const Color(0xFFFFC107),
    'low' => const Color(0xFF64B5F6),
    _ => const Color(0xFF90A4AE),
  };

  IconData _alertIcon(String type) => switch (type) {
    'frost' => Icons.ac_unit_rounded,
    'heat' => Icons.local_fire_department_rounded,
    'heavy_rain' => Icons.thunderstorm_rounded,
    'strong_wind' => Icons.air_rounded,
    'drought' => Icons.water_drop_outlined,
    'hail' => Icons.grain_rounded,
    'spraying_not_recommended' => Icons.sanitizer_outlined,
    _ => Icons.warning_amber_rounded,
  };

  String _severityLabel(BuildContext context, String severity) =>
      switch (severity) {
        'critical' => context.l10n.tr(fa: 'بحرانی', en: 'Critical'),
        'high' => context.l10n.tr(fa: 'خطر زیاد', en: 'High'),
        'medium' => context.l10n.tr(fa: 'نیازمند توجه', en: 'Medium'),
        'low' => context.l10n.tr(fa: 'کم', en: 'Low'),
        _ => context.l10n.tr(fa: 'اطلاع‌رسانی', en: 'Info'),
      };

  String _alertTitle(BuildContext context, WeatherAlertModel value) {
    if (context.l10n.isFa && value.title.isNotEmpty) return value.title;
    return switch (value.alertType) {
      'frost' => 'Frost warning',
      'heat' => 'Extreme heat warning',
      'heavy_rain' => 'Heavy rain warning',
      'strong_wind' => 'Strong wind warning',
      'drought' => 'Drought warning',
      'hail' => 'Hail warning',
      'spraying_not_recommended' => 'Spraying is not recommended',
      _ => context.l10n.tr(fa: value.title, en: 'Weather warning'),
    };
  }

  String _alertDescription(BuildContext context, WeatherAlertModel value) {
    if (context.l10n.isFa && value.body.isNotEmpty) return value.body;
    final payload = value.payload;
    return switch (value.alertType) {
      'frost' =>
        'Forecast temperature may reach ${payload['temperature_c'] ?? '--'}°C.',
      'heat' =>
        'Forecast temperature may reach ${payload['temperature_c'] ?? '--'}°C.',
      'heavy_rain' =>
        'Forecast precipitation is ${payload['precipitation_mm'] ?? '--'} mm.',
      'strong_wind' =>
        'Forecast wind speed is ${payload['wind_speed_mps'] ?? '--'} m/s.',
      'spraying_not_recommended' =>
        'Wind or precipitation probability makes this period unsuitable for spraying.',
      _ => 'Weather conditions may affect farm operations during this period.',
    };
  }

  String _alertAction(BuildContext context, String type) => switch (type) {
    'frost' => context.l10n.tr(
      fa: 'از محصولات حساس محافظت و تجهیزات مقابله با سرما را آماده کنید.',
      en: 'Protect sensitive crops and prepare frost protection equipment.',
    ),
    'heat' => context.l10n.tr(
      fa: 'آبیاری، سایه‌اندازی و تنش گرمایی محصول را بررسی کنید.',
      en: 'Review irrigation, shading, and crop heat stress.',
    ),
    'heavy_rain' => context.l10n.tr(
      fa: 'زهکشی را بررسی و عملیات مزرعه را تا بهبود شرایط متوقف کنید.',
      en:
          'Check drainage and postpone field operations until conditions improve.',
    ),
    'strong_wind' => context.l10n.tr(
      fa: 'سم‌پاشی و عملیات حساس به باد را متوقف کنید.',
      en: 'Stop spraying and other wind-sensitive operations.',
    ),
    'drought' => context.l10n.tr(
      fa: 'رطوبت خاک و برنامه آبیاری را بررسی کنید.',
      en: 'Review soil moisture and the irrigation plan.',
    ),
    'hail' => context.l10n.tr(
      fa: 'پوشش‌های محافظ و ایمنی تجهیزات را بررسی کنید.',
      en: 'Check protective covers and secure exposed equipment.',
    ),
    'spraying_not_recommended' => context.l10n.tr(
      fa: 'سم‌پاشی را به بازه‌ای با باد و احتمال بارش کمتر موکول کنید.',
      en: 'Move spraying to a period with lower wind and rain probability.',
    ),
    _ => context.l10n.tr(
      fa: 'پیش از عملیات، شرایط مزرعه و پیش‌بینی جدید را بررسی کنید.',
      en: 'Check field conditions and the latest forecast before operating.',
    ),
  };
}

class _OperationPlannerSection extends StatelessWidget {
  const _OperationPlannerSection({required this.plans});

  final List<WeatherOperationPlan> plans;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 30, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Text(
              context.l10n.tr(
                fa: 'پنجره مناسب عملیات مزرعه',
                en: 'Farm operation windows',
              ),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          const SizedBox(height: 10),
          FarmGlassCard(
            borderRadius: 18,
            opacity: 0.08,
            padding: const EdgeInsets.all(12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.info_outline_rounded,
                  color: Colors.white70,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    context.l10n.tr(
                      fa:
                          'این پیشنهاد فقط شرایط جوی ۴۸ ساعت آینده را می‌سنجد؛ رطوبت خاک، نوع محصول و دستور مصرف نهاده باید جداگانه بررسی شوند.',
                      en:
                          'These suggestions only assess the next 48 hours of weather. Soil moisture, crop needs, and product-label instructions must be checked separately.',
                    ),
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.72),
                      height: 1.5,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 196,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: plans.length,
              separatorBuilder: (context, index) => const SizedBox(width: 10),
              itemBuilder:
                  (context, index) => _OperationPlanCard(plan: plans[index]),
            ),
          ),
        ],
      ),
    );
  }
}

class _OperationPlanCard extends StatelessWidget {
  const _OperationPlanCard({required this.plan});

  final WeatherOperationPlan plan;

  @override
  Widget build(BuildContext context) {
    final accent = plan.isSuitable ? const Color(0xFF69F0AE) : Colors.amber;
    return SizedBox(
      width: 220,
      child: FarmGlassCard(
        borderRadius: 22,
        opacity: 0.1,
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(_operationIcon(plan.operation), color: accent, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _operationLabel(context, plan.operation),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Text(
                  _localizedNumber(context, '${plan.score}/100'),
                  style: TextStyle(
                    color: accent,
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              plan.isSuitable
                  ? context.l10n.tr(
                    fa: 'پنجره پیشنهادی',
                    en: 'Suggested window',
                  )
                  : context.l10n.tr(
                    fa: 'فعلاً نامناسب',
                    en: 'Currently unsuitable',
                  ),
              style: TextStyle(
                color: accent,
                fontWeight: FontWeight.w800,
                fontSize: 11,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              _windowLabel(context, plan),
              maxLines: 2,
              style: const TextStyle(
                color: Colors.white,
                height: 1.4,
                fontSize: 11,
              ),
            ),
            const Spacer(),
            Text(
              _reasonLabel(context, plan.reasonCodes.first),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.68),
                fontSize: 10,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _windowLabel(BuildContext context, WeatherOperationPlan value) {
    if (value.startsAt == null || value.endsAt == null) {
      return context.l10n.tr(
        fa: 'پیش‌بینی کافی نیست',
        en: 'Forecast is unavailable',
      );
    }
    return context.l10n.tr(
      fa:
          '${formatDate(context, value.startsAt!, showTime: true)} تا ${formatDate(context, value.endsAt!, showTime: true)}',
      en:
          '${formatDate(context, value.startsAt!, showTime: true)} to ${formatDate(context, value.endsAt!, showTime: true)}',
    );
  }

  IconData _operationIcon(WeatherOperationType value) => switch (value) {
    WeatherOperationType.spraying => Icons.sanitizer_outlined,
    WeatherOperationType.irrigation => Icons.water_drop_outlined,
    WeatherOperationType.fertilizing => Icons.grass_rounded,
    WeatherOperationType.harvest => Icons.agriculture_rounded,
    WeatherOperationType.machinery => Icons.precision_manufacturing_outlined,
  };

  String _operationLabel(BuildContext context, WeatherOperationType value) =>
      switch (value) {
        WeatherOperationType.spraying => context.l10n.tr(
          fa: 'سم‌پاشی',
          en: 'Spraying',
        ),
        WeatherOperationType.irrigation => context.l10n.tr(
          fa: 'آبیاری',
          en: 'Irrigation',
        ),
        WeatherOperationType.fertilizing => context.l10n.tr(
          fa: 'کوددهی',
          en: 'Fertilizing',
        ),
        WeatherOperationType.harvest => context.l10n.tr(
          fa: 'برداشت',
          en: 'Harvest',
        ),
        WeatherOperationType.machinery => context.l10n.tr(
          fa: 'ماشین‌آلات',
          en: 'Machinery',
        ),
      };

  String _reasonLabel(BuildContext context, String code) => switch (code) {
    'conditions_acceptable' => context.l10n.tr(
      fa: 'مانع جوی مهمی در این بازه دیده نشد.',
      en: 'No major weather obstacle was detected in this window.',
    ),
    'wind_blocking' => context.l10n.tr(
      fa: 'سرعت باد از حد ایمن این عملیات بیشتر است.',
      en: 'Wind speed exceeds the safe limit for this operation.',
    ),
    'wind_elevated' => context.l10n.tr(
      fa: 'باد می‌تواند دقت یا بازده عملیات را کاهش دهد.',
      en: 'Wind may reduce operation accuracy or efficiency.',
    ),
    'rain_probability_blocking' => context.l10n.tr(
      fa: 'احتمال بارش برای این عملیات زیاد است.',
      en: 'Rain probability is too high for this operation.',
    ),
    'rain_probability_elevated' => context.l10n.tr(
      fa: 'احتمال بارش نیازمند احتیاط است.',
      en: 'Rain probability requires caution.',
    ),
    'rain_expected' => context.l10n.tr(
      fa: 'در این بازه بارش پیش‌بینی شده است.',
      en: 'Rain is forecast during this window.',
    ),
    'heavy_rain_expected' => context.l10n.tr(
      fa: 'بارش سنگین می‌تواند عملیات را مختل کند.',
      en: 'Heavy rain may disrupt the operation.',
    ),
    'humidity_high' || 'humidity_elevated' => context.l10n.tr(
      fa: 'رطوبت هوا برای این عملیات بالا است.',
      en: 'Humidity is elevated for this operation.',
    ),
    'heat_evaporation' => context.l10n.tr(
      fa: 'گرما می‌تواند اتلاف تبخیری را افزایش دهد.',
      en: 'Heat may increase evaporation losses.',
    ),
    'temperature_risk' => context.l10n.tr(
      fa: 'دما برای این عملیات در بازه مطلوب نیست.',
      en: 'Temperature is outside the preferred range.',
    ),
    _ => context.l10n.tr(
      fa: 'داده پیش‌بینی کافی برای پیشنهاد مطمئن نیست.',
      en: 'Forecast data is insufficient for a reliable suggestion.',
    ),
  };
}

class _DailyForecastSummary {
  const _DailyForecastSummary({
    required this.date,
    required this.minTemperature,
    required this.maxTemperature,
    required this.maxPrecipitationProbability,
    required this.totalPrecipitationMm,
    required this.averageHumidity,
    required this.maxWindSpeed,
    required this.condition,
  });

  final DateTime date;
  final double? minTemperature;
  final double? maxTemperature;
  final double? maxPrecipitationProbability;
  final double? totalPrecipitationMm;
  final double? averageHumidity;
  final double? maxWindSpeed;
  final String? condition;

  factory _DailyForecastSummary.fromRows(
    DateTime date,
    List<WeatherForecastModel> rows,
  ) {
    final temperatures = <double>[];
    final probabilities = <double>[];
    final precipitation = <double>[];
    final humidities = <double>[];
    final winds = <double>[];
    final conditions = <String, int>{};

    for (final row in rows) {
      final temperature = double.tryParse(row.temperatureC ?? '');
      final minTemperature = double.tryParse(row.minTemperatureC ?? '');
      final maxTemperature = double.tryParse(row.maxTemperatureC ?? '');
      if (temperature != null) temperatures.add(temperature);
      if (minTemperature != null) temperatures.add(minTemperature);
      if (maxTemperature != null) temperatures.add(maxTemperature);

      final probability = double.tryParse(row.precipitationProbability ?? '');
      if (probability != null) probabilities.add(probability);
      final rain = double.tryParse(row.precipitationMm ?? '');
      if (rain != null) precipitation.add(rain);
      final humidity = double.tryParse(row.humidityPercent ?? '');
      if (humidity != null) humidities.add(humidity);
      final wind = double.tryParse(row.windSpeedMps ?? '');
      if (wind != null) winds.add(wind);
      final condition = row.conditionText?.trim();
      if (condition != null && condition.isNotEmpty) {
        conditions[condition] = (conditions[condition] ?? 0) + 1;
      }
    }

    double? minimum(List<double> values) =>
        values.isEmpty ? null : values.reduce((a, b) => a < b ? a : b);
    double? maximum(List<double> values) =>
        values.isEmpty ? null : values.reduce((a, b) => a > b ? a : b);
    double? average(List<double> values) =>
        values.isEmpty ? null : values.reduce((a, b) => a + b) / values.length;
    final sortedConditions =
        conditions.entries.toList()..sort((a, b) => b.value.compareTo(a.value));

    return _DailyForecastSummary(
      date: date,
      minTemperature: minimum(temperatures),
      maxTemperature: maximum(temperatures),
      maxPrecipitationProbability: maximum(probabilities),
      totalPrecipitationMm:
          precipitation.isEmpty ? null : precipitation.reduce((a, b) => a + b),
      averageHumidity: average(humidities),
      maxWindSpeed: maximum(winds),
      condition: sortedConditions.isEmpty ? null : sortedConditions.first.key,
    );
  }
}

class _DailyForecastCard extends StatelessWidget {
  const _DailyForecastCard({required this.summary});

  final _DailyForecastSummary summary;

  @override
  Widget build(BuildContext context) {
    final rainProbability = summary.maxPrecipitationProbability;
    final probabilityPercent =
        rainProbability == null
            ? null
            : (rainProbability <= 1 ? rainProbability * 100 : rainProbability)
                .round();
    return SizedBox(
      width: 190,
      child: FarmGlassCard(
        borderRadius: 24,
        opacity: 0.1,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              formatDate(context, summary.date),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              summary.condition ??
                  context.l10n.tr(fa: 'بدون توضیح', en: 'No description'),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.68),
                fontSize: 11,
              ),
            ),
            const Spacer(),
            Row(
              children: [
                const Icon(
                  Icons.thermostat_rounded,
                  color: Colors.orangeAccent,
                  size: 20,
                ),
                const SizedBox(width: 6),
                Text(
                  _localizedNumber(
                    context,
                    '${summary.maxTemperature?.round() ?? '--'}° / ${summary.minTemperature?.round() ?? '--'}°',
                  ),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            _DailyMetricLine(
              icon: Icons.water_drop_outlined,
              label: context.l10n.tr(fa: 'بارش', en: 'Rain'),
              value: _localizedNumber(
                context,
                '${probabilityPercent == null ? '--' : '$probabilityPercent%'} · ${summary.totalPrecipitationMm?.toStringAsFixed(1) ?? '--'} mm',
              ),
            ),
            const SizedBox(height: 6),
            _DailyMetricLine(
              icon: Icons.air_rounded,
              label: context.l10n.tr(fa: 'بیشینه باد', en: 'Peak wind'),
              value: _localizedNumber(
                context,
                '${summary.maxWindSpeed?.toStringAsFixed(1) ?? '--'} m/s',
              ),
            ),
            const SizedBox(height: 6),
            _DailyMetricLine(
              icon: Icons.opacity_rounded,
              label: context.l10n.tr(fa: 'میانگین رطوبت', en: 'Avg humidity'),
              value: _localizedNumber(
                context,
                '${summary.averageHumidity?.round() ?? '--'}%',
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DailyMetricLine extends StatelessWidget {
  const _DailyMetricLine({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: Colors.white70, size: 15),
        const SizedBox(width: 5),
        Expanded(
          child: Text(
            label,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.64),
              fontSize: 9,
            ),
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 10,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _PositionedOrb extends StatelessWidget {
  final double? top, right, bottom, left;
  final Color color;
  const _PositionedOrb({
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
        width: 300,
        height: 300,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      ),
    );
  }
}

class _LocationPickerSheet extends ConsumerStatefulWidget {
  const _LocationPickerSheet();
  @override
  ConsumerState<_LocationPickerSheet> createState() =>
      _LocationPickerSheetState();
}

class _LocationPickerSheetState extends ConsumerState<_LocationPickerSheet> {
  int? _provinceId;
  int? _cityId;
  late final Future<List<_FarmPlotOption>> _farmPlotsFuture;

  @override
  void initState() {
    super.initState();
    _farmPlotsFuture = _loadFarmPlots(ref.read(farmRepositoryProvider));
  }

  @override
  Widget build(BuildContext context) {
    final geoRepo = ref.watch(geoRepositoryProvider);
    final weatherState = ref.watch(weatherControllerProvider);
    final isWide = MediaQuery.of(context).size.width > 900;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Align(
      alignment: Alignment.bottomCenter,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 14),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxWidth: isWide ? 450 : double.infinity,
            maxHeight: MediaQuery.sizeOf(context).height * 0.86,
          ),
          child: Container(
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF101810) : Colors.white,
              borderRadius: BorderRadius.circular(32),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.3),
                  blurRadius: 20,
                ),
              ],
            ),
            padding: const EdgeInsets.all(24),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: isDark ? Colors.white24 : Colors.black12,
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    context.l10n.tr(
                      fa: 'تنظیم موقعیت پایش',
                      en: 'Monitoring location',
                    ),
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      color: isDark ? Colors.white : const Color(0xFF1B5E20),
                    ),
                  ),
                  const SizedBox(height: 24),

                  if (weatherState.locations.isNotEmpty) ...[
                    Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Text(
                        context.l10n.tr(
                          fa: 'موقعیت‌های ذخیره‌شده',
                          en: 'Saved locations',
                        ),
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      height: 48,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        itemCount: weatherState.locations.length,
                        separatorBuilder:
                            (context, index) => const SizedBox(width: 8),
                        itemBuilder: (context, index) {
                          final location = weatherState.locations[index];
                          final selected =
                              !weatherState.isFarmSource &&
                              weatherState.selectedLocation?.id == location.id;
                          return ChoiceChip(
                            selected: selected,
                            avatar: Icon(
                              location.locationType == 'gps'
                                  ? Icons.my_location_rounded
                                  : Icons.location_city_rounded,
                              size: 17,
                            ),
                            label: Text(location.displayName),
                            onSelected: (_) {
                              Navigator.pop(context);
                              ref
                                  .read(weatherControllerProvider.notifier)
                                  .loadLocation(location);
                            },
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: Text(
                      context.l10n.tr(
                        fa: 'مزارع و قطعه‌های من',
                        en: 'My farms and plots',
                      ),
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  FutureBuilder<List<_FarmPlotOption>>(
                    future: _farmPlotsFuture,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const FarmLoadingView(compact: true);
                      }
                      final options =
                          snapshot.data ?? const <_FarmPlotOption>[];
                      if (options.isEmpty) {
                        return Align(
                          alignment: AlignmentDirectional.centerStart,
                          child: Text(
                            context.l10n.tr(
                              fa: 'قطعه دارای مختصات برای پایش پیدا نشد.',
                              en: 'No plot with coordinates is available.',
                            ),
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        );
                      }
                      return SizedBox(
                        height: 56,
                        child: ListView.separated(
                          scrollDirection: Axis.horizontal,
                          itemCount: options.length,
                          separatorBuilder:
                              (context, index) => const SizedBox(width: 8),
                          itemBuilder: (context, index) {
                            final option = options[index];
                            final selected =
                                weatherState.selectedFarmId == option.farm.id &&
                                weatherState.selectedPlotId == option.plot.id;
                            return ChoiceChip(
                              selected: selected,
                              avatar: const Icon(
                                Icons.agriculture_rounded,
                                size: 18,
                              ),
                              label: Text(
                                '${option.farm.name} · ${option.plot.name}',
                              ),
                              onSelected: (_) {
                                Navigator.pop(context);
                                ref
                                    .read(weatherControllerProvider.notifier)
                                    .loadFarmPlot(
                                      farmId: option.farm.id,
                                      plotId: option.plot.id,
                                      farmName: option.farm.name,
                                      plotName: option.plot.name,
                                    );
                              },
                            );
                          },
                        ),
                      );
                    },
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 20),
                    child: Divider(
                      height: 1,
                      color: isDark ? Colors.white12 : Colors.black12,
                    ),
                  ),

                  _PickerOption(
                    isDark: isDark,
                    icon: Icons.my_location_rounded,
                    title: context.l10n.tr(
                      fa: 'موقعیت آنی (GPS)',
                      en: 'Current location (GPS)',
                    ),
                    subtitle: context.l10n.tr(
                      fa: 'دقیق‌ترین پایش بر اساس مختصات فعلی',
                      en: 'Most accurate monitoring for your coordinates',
                    ),
                    onTap: () => _useCurrentLocation(context),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 20),
                    child: Divider(
                      height: 1,
                      color: isDark ? Colors.white12 : Colors.black12,
                    ),
                  ),
                  Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: Text(
                      context.l10n.tr(
                        fa: 'انتخاب دستی منطقه',
                        en: 'Choose a region manually',
                      ),
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w900,
                        color: isDark ? Colors.white70 : Colors.black54,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Theme(
                    data: Theme.of(context).copyWith(
                      canvasColor:
                          isDark ? const Color(0xFF1B5E20) : Colors.white,
                    ),
                    child: Column(
                      children: [
                        FutureBuilder<List<GeoProvince>>(
                          future: geoRepo.getProvinces(),
                          builder: (context, snapshot) {
                            final provinces = snapshot.data ?? [];
                            return DropdownButtonFormField<int>(
                              dropdownColor:
                                  isDark
                                      ? const Color(0xFF1B5E20)
                                      : Colors.white,
                              style: TextStyle(
                                color: isDark ? Colors.white : Colors.black87,
                                fontFamily: 'IRYekan',
                              ),
                              initialValue: _provinceId,
                              decoration: InputDecoration(
                                labelText: context.l10n.tr(
                                  fa: 'استان',
                                  en: 'Province',
                                ),
                                labelStyle: TextStyle(
                                  color:
                                      isDark ? Colors.white70 : Colors.black45,
                                ),
                                filled: true,
                                fillColor:
                                    isDark
                                        ? Colors.white.withValues(alpha: 0.05)
                                        : Colors.black.withValues(alpha: 0.03),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(14),
                                  borderSide: BorderSide(
                                    color:
                                        isDark
                                            ? Colors.white12
                                            : Colors.black12,
                                  ),
                                ),
                              ),
                              items:
                                  provinces
                                      .map(
                                        (p) => DropdownMenuItem(
                                          value: p.id,
                                          child: Text(p.name),
                                        ),
                                      )
                                      .toList(),
                              onChanged:
                                  (v) => setState(() {
                                    _provinceId = v;
                                    _cityId = null;
                                  }),
                            );
                          },
                        ),
                        const SizedBox(height: 12),
                        if (_provinceId != null)
                          FutureBuilder<List<GeoCity>>(
                            future: geoRepo.getCities(provinceId: _provinceId),
                            builder: (context, snapshot) {
                              final cities = snapshot.data ?? [];
                              return DropdownButtonFormField<int>(
                                dropdownColor:
                                    isDark
                                        ? const Color(0xFF1B5E20)
                                        : Colors.white,
                                style: TextStyle(
                                  color: isDark ? Colors.white : Colors.black87,
                                  fontFamily: 'IRYekan',
                                ),
                                initialValue: _cityId,
                                decoration: InputDecoration(
                                  labelText: context.l10n.tr(
                                    fa: 'شهر',
                                    en: 'City',
                                  ),
                                  labelStyle: TextStyle(
                                    color:
                                        isDark
                                            ? Colors.white70
                                            : Colors.black45,
                                  ),
                                  filled: true,
                                  fillColor:
                                      isDark
                                          ? Colors.white.withValues(alpha: 0.05)
                                          : Colors.black.withValues(
                                            alpha: 0.03,
                                          ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(14),
                                    borderSide: BorderSide(
                                      color:
                                          isDark
                                              ? Colors.white12
                                              : Colors.black12,
                                    ),
                                  ),
                                ),
                                items:
                                    cities
                                        .map(
                                          (c) => DropdownMenuItem(
                                            value: c.id,
                                            child: Text(c.name),
                                          ),
                                        )
                                        .toList(),
                                onChanged:
                                    (v) => setState(() {
                                      _cityId = v;
                                    }),
                              );
                            },
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),
                  if (_cityId != null)
                    FilledButton(
                      onPressed: () async {
                        final provinceId = _provinceId;
                        final cityId = _cityId;
                        if (provinceId == null || cityId == null) return;
                        Navigator.pop(context);
                        await ref
                            .read(weatherControllerProvider.notifier)
                            .createGeoLocation(
                              provinceId: provinceId,
                              cityId: cityId,
                            );
                      },
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF2E7D32),
                        minimumSize: const Size(double.infinity, 56),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      child: Text(
                        context.l10n.tr(
                          fa: 'تأیید و مشاهده آب‌وهوا',
                          en: 'Confirm and view weather',
                        ),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _useCurrentLocation(BuildContext sheetContext) async {
    final l10n = context.l10n;
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw _LocationMessage(
          l10n.tr(
            fa:
                'اجازهٔ دسترسی به موقعیت داده نشد. دسترسی Location را در مرورگر فعال کنید.',
            en:
                'Location permission was denied. Enable Location access in your browser.',
          ),
        );
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );
      if (!mounted || !sheetContext.mounted) return;
      Navigator.pop(sheetContext);
      await ref
          .read(weatherControllerProvider.notifier)
          .createGpsLocation(
            latitude: position.latitude,
            longitude: position.longitude,
            displayName: l10n.tr(
              fa: 'موقعیت فعلی من',
              en: 'My current location',
            ),
          );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            error is _LocationMessage
                ? error.message
                : l10n.tr(
                  fa:
                      'موقعیت فعلی دریافت نشد. دسترسی Location مرورگر را بررسی کنید.',
                  en:
                      'Current location could not be read. Check browser Location access.',
                ),
          ),
        ),
      );
    }
  }

  Future<List<_FarmPlotOption>> _loadFarmPlots(
    FarmRepository repository,
  ) async {
    try {
      final farms = await repository.farms();
      final values = await Future.wait(
        farms.map((farm) async {
          final plots = await repository.plots(farm.id);
          return plots
              .where((plot) => plot.latitude != null && plot.longitude != null)
              .map((plot) => _FarmPlotOption(farm: farm, plot: plot));
        }),
      );
      return values.expand((items) => items).toList();
    } catch (_) {
      return const [];
    }
  }
}

class _FarmPlotOption {
  const _FarmPlotOption({required this.farm, required this.plot});

  final FarmModel farm;
  final FarmPlotModel plot;
}

class _LocationMessage implements Exception {
  const _LocationMessage(this.message);
  final String message;
}

class _PickerOption extends StatelessWidget {
  final IconData icon;
  final String title, subtitle;
  final VoidCallback onTap;
  final bool isDark;
  const _PickerOption({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color:
                  isDark
                      ? Colors.white.withValues(alpha: 0.1)
                      : const Color(0xFF2E7D32).withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: isDark ? Colors.white : const Color(0xFF2E7D32),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: isDark ? Colors.white : Colors.black87,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    color:
                        isDark
                            ? Colors.white.withValues(alpha: 0.6)
                            : Colors.black45,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label, value;
  final IconData icon;
  const _MetricCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return FarmGlassCard(
      borderRadius: 24,
      opacity: 0.08,
      padding: const EdgeInsets.all(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white.withValues(alpha: 0.8), size: 28),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.5),
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}

class _HourlyForecastItem extends StatelessWidget {
  final WeatherForecastModel forecast;
  final bool isNight;
  const _HourlyForecastItem({required this.forecast, required this.isNight});

  @override
  Widget build(BuildContext context) {
    final parsedTime = DateTime.tryParse(forecast.forecastTime)?.toLocal();
    final timeLabel =
        parsedTime == null
            ? '--:--'
            : MaterialLocalizations.of(context).formatTimeOfDay(
              TimeOfDay.fromDateTime(parsedTime),
              alwaysUse24HourFormat: true,
            );
    return Container(
      width: 104,
      margin: const EdgeInsets.only(left: 12),
      child: FarmGlassCard(
        borderRadius: 24,
        opacity: 0.08,
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _localizedNumber(context, timeLabel),
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.6),
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Icon(
              isNight ? Icons.nights_stay_rounded : Icons.wb_cloudy_rounded,
              color: Colors.white.withValues(alpha: 0.9),
              size: 24,
            ),
            const SizedBox(height: 10),
            Text(
              _localizedNumber(
                context,
                '${double.tryParse(forecast.temperatureC ?? '')?.round() ?? '--'}°',
              ),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w900,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 6),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.water_drop_outlined,
                  color: Colors.lightBlueAccent,
                  size: 13,
                ),
                const SizedBox(width: 3),
                Text(
                  _forecastRainLabel(context, forecast),
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.72),
                    fontSize: 9,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              _localizedNumber(context, '${forecast.windSpeedMps ?? '--'} m/s'),
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.6),
                fontSize: 9,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _forecastRainLabel(
    BuildContext context,
    WeatherForecastModel forecast,
  ) {
    final value = double.tryParse(forecast.precipitationProbability ?? '');
    if (value == null) return '--';
    final percent = value <= 1 ? value * 100 : value;
    return _localizedNumber(context, '${percent.round()}%');
  }
}

class _WeatherIcon extends StatelessWidget {
  final String? condition;
  final bool isNight;
  const _WeatherIcon({this.condition, required this.isNight});

  @override
  Widget build(BuildContext context) {
    final cond = (condition ?? '').toLowerCase();
    IconData icon =
        isNight ? Icons.nights_stay_rounded : Icons.wb_sunny_rounded;
    Color color = isNight ? Colors.indigoAccent[100]! : Colors.yellowAccent;

    if (cond.contains('rain') || cond.contains('باران')) {
      icon = Icons.umbrella_rounded;
      color = Colors.lightBlueAccent;
    } else if (cond.contains('cloud') || cond.contains('ابری')) {
      icon = Icons.wb_cloudy_rounded;
      color = Colors.white;
    }

    return Icon(
      icon,
      color: color,
      size: 90,
      shadows: [Shadow(color: color.withValues(alpha: 0.5), blurRadius: 40)],
    );
  }
}
