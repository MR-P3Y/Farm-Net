import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
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

    Future.microtask(() {
      ref.read(weatherControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(weatherControllerProvider);

    return Scaffold(
      appBar: FarmAppBar(
        title: 'آب‌وهوا',
        actions: [
          IconButton(
            onPressed:
                state.isSaving
                    ? null
                    : () {
                      ref
                          .read(weatherControllerProvider.notifier)
                          .refreshSelected();
                    },
            icon: const Icon(Icons.refresh),
            tooltip: 'بروزرسانی',
          ),
        ],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child:
                      state.isLoading
                          ? const FarmLoadingView()
                          : state.locations.isEmpty
                          ? const FarmEmptyView(
                            message:
                                'هنوز موقعیت آب‌وهوا برای نمایش وجود ندارد.',
                          )
                          : Column(
                            children: [
                              if (state.errorMessage != null) ...[
                                _ErrorBox(message: state.errorMessage!),
                                SizedBox(height: r.v(12)),
                              ],
                              _LocationSelector(
                                locations: state.locations,
                                selected: state.selectedLocation,
                                onChanged: (location) {
                                  if (location == null) return;
                                  ref
                                      .read(weatherControllerProvider.notifier)
                                      .loadLocation(location);
                                },
                              ),
                              SizedBox(height: r.v(12)),
                              Expanded(
                                child: RefreshIndicator(
                                  onRefresh:
                                      () =>
                                          ref
                                              .read(
                                                weatherControllerProvider
                                                    .notifier,
                                              )
                                              .refreshSelected(),
                                  child: ListView(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      _CurrentWeatherCard(
                                        current: state.current,
                                        location: state.selectedLocation,
                                      ),
                                      SizedBox(height: r.v(12)),
                                      _AlertsSection(alerts: state.alerts),
                                      SizedBox(height: r.v(12)),
                                      _ForecastSection(
                                        forecasts: state.forecasts,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                ),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: state.isSaving ? null : () => _showGpsDialog(context),
        icon: const Icon(Icons.my_location_outlined),
        label: const Text('GPS'),
      ),
    );
  }

  Future<void> _showGpsDialog(BuildContext context) async {
    final latController = TextEditingController();
    final lonController = TextEditingController();
    final nameController = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: const Text('ثبت موقعیت GPS'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'نام موقعیت',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: latController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                    signed: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Latitude',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: lonController,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                    signed: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Longitude',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () async {
                final lat = double.tryParse(latController.text.trim());
                final lon = double.tryParse(lonController.text.trim());

                if (lat == null || lon == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('مختصات معتبر نیست.')),
                  );
                  return;
                }

                await ref
                    .read(weatherControllerProvider.notifier)
                    .createGpsLocation(
                      latitude: lat,
                      longitude: lon,
                      displayName:
                          nameController.text.trim().isEmpty
                              ? null
                              : nameController.text.trim(),
                    );

                if (context.mounted) Navigator.pop(context);
              },
              child: const Text('ثبت'),
            ),
          ],
        );
      },
    );

    latController.dispose();
    lonController.dispose();
    nameController.dispose();
  }
}

class _LocationSelector extends StatelessWidget {
  const _LocationSelector({
    required this.locations,
    required this.selected,
    required this.onChanged,
  });

  final List<WeatherLocationModel> locations;
  final WeatherLocationModel? selected;
  final ValueChanged<WeatherLocationModel?> onChanged;

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<WeatherLocationModel>(
      initialValue: selected,
      isExpanded: true,
      decoration: const InputDecoration(
        labelText: 'موقعیت',
        border: OutlineInputBorder(),
      ),
      items:
          locations
              .map(
                (location) => DropdownMenuItem(
                  value: location,
                  child: Text(
                    location.displayName,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              )
              .toList(),
      onChanged: onChanged,
    );
  }
}

class _CurrentWeatherCard extends StatelessWidget {
  const _CurrentWeatherCard({required this.current, required this.location});

  final WeatherSnapshotModel? current;
  final WeatherLocationModel? location;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final snapshot = current;

    if (snapshot == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'داده فعلی موجود نیست. بروزرسانی را بزنید.',
            style: theme.textTheme.bodyMedium,
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              location?.displayName ?? 'آب‌وهوا',
              style: theme.textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Text(
              '${snapshot.temperatureC ?? '-'}°C',
              style: theme.textTheme.displaySmall,
            ),
            const SizedBox(height: 8),
            Text(snapshot.conditionText ?? 'وضعیت نامشخص'),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text('رطوبت: ${snapshot.humidityPercent ?? '-'}٪')),
                Chip(label: Text('باد: ${snapshot.windSpeedMps ?? '-'} m/s')),
                Chip(label: Text('فشار: ${snapshot.pressureHpa ?? '-'} hPa')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _AlertsSection extends StatelessWidget {
  const _AlertsSection({required this.alerts});

  final List<WeatherAlertModel> alerts;

  @override
  Widget build(BuildContext context) {
    if (alerts.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('هشدار فعالی وجود ندارد.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('هشدارها', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ...alerts.map(
          (alert) => Card(
            child: ListTile(
              leading: const Icon(Icons.warning_amber_outlined),
              title: Text(alert.title),
              subtitle: Text(alert.body),
              trailing: Chip(label: Text(alert.severity)),
            ),
          ),
        ),
      ],
    );
  }
}

class _ForecastSection extends StatelessWidget {
  const _ForecastSection({required this.forecasts});

  final List<WeatherForecastModel> forecasts;

  @override
  Widget build(BuildContext context) {
    if (forecasts.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('پیش‌بینی موجود نیست.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('پیش‌بینی', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        ...forecasts
            .take(12)
            .map(
              (item) => Card(
                child: ListTile(
                  leading: const Icon(Icons.cloud_outlined),
                  title: Text('${item.temperatureC ?? '-'}°C'),
                  subtitle: Text(item.conditionText ?? item.forecastTime),
                  trailing: Text(
                    item.windSpeedMps == null
                        ? '-'
                        : '${item.windSpeedMps} m/s',
                  ),
                ),
              ),
            ),
      ],
    );
  }
}

class _ErrorBox extends StatelessWidget {
  const _ErrorBox({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Card(
      color: colors.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(message, style: TextStyle(color: colors.onErrorContainer)),
      ),
    );
  }
}
