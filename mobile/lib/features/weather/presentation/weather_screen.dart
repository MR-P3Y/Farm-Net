import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';

import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_circular_glass_button.dart';
import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/weather_models.dart';
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
                        Column(
                          children: [
                            Text(
                              state.selectedLocation?.displayName ??
                                  'موقعیت نامشخص',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w900,
                                fontSize: 18,
                                shadows: [
                                  Shadow(color: Colors.black26, blurRadius: 10),
                                ],
                              ),
                            ),
                            Text(
                              isActuallyNight ? 'پایش شبانه' : 'پایش روزانه',
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.7),
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                        FarmCircularGlassButton(
                          icon: Icons.map_rounded,
                          onTap: () => _showLocationPicker(context),
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
                                    color: Colors.white.withValues(alpha: 0.15),
                                    blurRadius: 80,
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              '${double.tryParse(state.current?.temperatureC ?? '')?.toInt() ?? '--'}°',
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
                                  ? 'در حال دریافت اطلاعات هواشناسی...'
                                  : 'اطلاعات هواشناسی دریافت نشد'),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1.2,
                          ),
                        ),
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
                              const Text(
                                'توصیه هوشمند امروز',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w900,
                                  fontSize: 15,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            _getFarmAdvice(state.current),
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
                        label: 'رطوبت',
                        value: '${state.current?.humidityPercent ?? '--'}٪',
                        icon: Icons.water_drop_rounded,
                      ),
                      _MetricCard(
                        label: 'سرعت باد',
                        value: '${state.current?.windSpeedMps ?? '--'} m/s',
                        icon: Icons.air_rounded,
                      ),
                      _MetricCard(
                        label: 'فشار',
                        value: (state.current?.pressureHpa ?? '--').toString(),
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
                        const Text(
                          'پیش‌بینی ساعتی',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        Text(
                          '۱۲ ساعت آینده',
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
                    height: 130,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      physics: const BouncingScrollPhysics(),
                      itemCount: state.forecasts.length.clamp(0, 12),
                      itemBuilder: (context, index) {
                        final forecast = state.forecasts[index];
                        return _HourlyForecastItem(
                          forecast: forecast,
                          isNight: isActuallyNight,
                        );
                      },
                    ),
                  ),
                ),

                const SliverToBoxAdapter(child: SizedBox(height: 40)),
              ],
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

  String _getFarmAdvice(WeatherSnapshotModel? current) {
    if (current == null) return 'در حال دریافت اطلاعات مزرعه...';
    final wind = double.tryParse(current.windSpeedMps ?? '0') ?? 0;
    if (wind > 5) {
      return 'هشدار: سرعت باد برای سم‌پاشی زیاد است. سم‌پاشی را به ساعات آرام‌تر (غروب یا سپیده‌دم) موکول کنید.';
    }
    return 'شرایط جوی برای تغذیه برگی و آبیاری تحت‌فشار بسیار مساعد است. رطوبت هوا در بازه بهینه قرار دارد.';
  }

  void _showLocationPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const _LocationPickerSheet(),
    );
  }
}

class _Atmosphere {
  final List<Color> colors;
  final Color accentColor;
  _Atmosphere({required this.colors, required this.accentColor});
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

  @override
  Widget build(BuildContext context) {
    final geoRepo = ref.watch(geoRepositoryProvider);
    final isWide = MediaQuery.of(context).size.width > 900;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: isWide ? 450 : double.infinity),
        child: Container(
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF101810) : Colors.white,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(35)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 20,
              ),
            ],
          ),
          padding: const EdgeInsets.all(28),
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
                'تنظیم موقعیت پایش',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: isDark ? Colors.white : const Color(0xFF1B5E20),
                ),
              ),
              const SizedBox(height: 24),

              _PickerOption(
                isDark: isDark,
                icon: Icons.my_location_rounded,
                title: 'موقعیت آنی (GPS)',
                subtitle: 'دقیق‌ترین پایش بر اساس مختصات فعلی',
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
                  'انتخاب دستی منطقه',
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
                  canvasColor: isDark ? const Color(0xFF1B5E20) : Colors.white,
                ),
                child: Column(
                  children: [
                    FutureBuilder<List<GeoProvince>>(
                      future: geoRepo.getProvinces(),
                      builder: (context, snapshot) {
                        final provinces = snapshot.data ?? [];
                        return DropdownButtonFormField<int>(
                          dropdownColor:
                              isDark ? const Color(0xFF1B5E20) : Colors.white,
                          style: TextStyle(
                            color: isDark ? Colors.white : Colors.black87,
                            fontFamily: 'IRYekan',
                          ),
                          initialValue: _provinceId,
                          decoration: InputDecoration(
                            labelText: 'استان',
                            labelStyle: TextStyle(
                              color: isDark ? Colors.white70 : Colors.black45,
                            ),
                            filled: true,
                            fillColor:
                                isDark
                                    ? Colors.white.withValues(alpha: 0.05)
                                    : Colors.black.withValues(alpha: 0.03),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(14),
                              borderSide: BorderSide(
                                color: isDark ? Colors.white12 : Colors.black12,
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
                                isDark ? const Color(0xFF1B5E20) : Colors.white,
                            style: TextStyle(
                              color: isDark ? Colors.white : Colors.black87,
                              fontFamily: 'IRYekan',
                            ),
                            initialValue: _cityId,
                            decoration: InputDecoration(
                              labelText: 'شهر',
                              labelStyle: TextStyle(
                                color: isDark ? Colors.white70 : Colors.black45,
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
                                      isDark ? Colors.white12 : Colors.black12,
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
                  child: const Text(
                    'تایید و مشاهده آب‌وهوا',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _useCurrentLocation(BuildContext sheetContext) async {
    try {
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw const _LocationMessage(
          'اجازهٔ دسترسی به موقعیت داده نشد. دسترسی Location را در مرورگر فعال کنید.',
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
            displayName: 'موقعیت فعلی من',
          );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            error is _LocationMessage
                ? error.message
                : 'موقعیت فعلی دریافت نشد. دسترسی Location مرورگر را بررسی کنید.',
          ),
        ),
      );
    }
  }
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
    return Container(
      width: 75,
      margin: const EdgeInsets.only(left: 12),
      child: FarmGlassCard(
        borderRadius: 24,
        opacity: 0.08,
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              forecast.forecastTime.split(' ').last.substring(0, 5),
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
              '${double.tryParse(forecast.temperatureC ?? '')?.toInt() ?? '--'}°',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w900,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
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
