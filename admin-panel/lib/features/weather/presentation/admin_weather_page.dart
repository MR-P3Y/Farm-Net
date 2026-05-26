import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_weather_models.dart';
import '../state/admin_weather_controller.dart';

class AdminWeatherPage extends ConsumerStatefulWidget {
  const AdminWeatherPage({super.key});

  @override
  ConsumerState<AdminWeatherPage> createState() => _AdminWeatherPageState();
}

class _AdminWeatherPageState extends ConsumerState<AdminWeatherPage> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminWeatherControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminWeatherControllerProvider);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return Padding(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    'مدیریت آب‌وهوا',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Refresh',
                    onPressed:
                        state.isSaving
                            ? null
                            : () =>
                                ref
                                    .read(
                                      adminWeatherControllerProvider.notifier,
                                    )
                                    .load(),
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 16),
              Expanded(
                child:
                    state.isLoading
                        ? const AdminLoadingView()
                        : ListView(
                          children: [
                            _ProviderConfigsSection(
                              configs: state.providerConfigs,
                            ),
                            const SizedBox(height: 16),
                            _LocationsSection(
                              locations: state.locations,
                              selected: state.selectedLocation,
                              isSaving: state.isSaving,
                            ),
                            const SizedBox(height: 16),
                            _CacheStatusSection(status: state.cacheStatus),
                            const SizedBox(height: 16),
                            _AlertRulesSection(
                              rules: state.alertRules,
                              isSaving: state.isSaving,
                            ),
                            const SizedBox(height: 16),
                            _AlertsSection(alerts: state.alerts),
                            if (state.lastEvaluation != null) ...[
                              const SizedBox(height: 16),
                              _EvaluationBox(result: state.lastEvaluation!),
                            ],
                          ],
                        ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProviderConfigsSection extends ConsumerWidget {
  const _ProviderConfigsSection({required this.configs});

  final List<AdminWeatherProviderConfig> configs;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (configs.isEmpty) {
      return const AdminEmptyView(message: 'Provider config موجود نیست.');
    }

    return _Section(
      title: 'Providerها',
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('Provider')),
          DataColumn(label: Text('Active')),
          DataColumn(label: Text('Priority')),
          DataColumn(label: Text('Base URL')),
          DataColumn(label: Text('API Key Ref')),
          DataColumn(label: Text('Action')),
        ],
        rows:
            configs.map((config) {
              return DataRow(
                cells: [
                  DataCell(Text(config.provider)),
                  DataCell(Text(config.isActive ? 'yes' : 'no')),
                  DataCell(Text(config.priority.toString())),
                  DataCell(Text(config.baseUrl ?? '-')),
                  DataCell(Text(config.apiKeyRef ?? '-')),
                  DataCell(
                    TextButton.icon(
                      onPressed:
                          () => _openProviderDialog(context, ref, config),
                      icon: const Icon(Icons.edit_outlined),
                      label: const Text('ویرایش'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }

  Future<void> _openProviderDialog(
    BuildContext context,
    WidgetRef ref,
    AdminWeatherProviderConfig config,
  ) async {
    final priorityController = TextEditingController(
      text: config.priority.toString(),
    );
    final baseUrlController = TextEditingController(text: config.baseUrl ?? '');
    final apiKeyRefController = TextEditingController(
      text: config.apiKeyRef ?? '',
    );
    var isActive = config.isActive;

    await showDialog<void>(
      context: context,
      builder: (_) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text('ویرایش ${config.provider}'),
              content: SizedBox(
                width: 560,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SwitchListTile(
                        value: isActive,
                        title: const Text('فعال'),
                        onChanged: (value) {
                          setState(() => isActive = value);
                        },
                      ),
                      TextField(
                        controller: priorityController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Priority',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: baseUrlController,
                        decoration: const InputDecoration(
                          labelText: 'Base URL',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: apiKeyRefController,
                        decoration: const InputDecoration(
                          labelText: 'API Key Ref',
                          hintText: 'OPENWEATHER_API_KEY',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'کلید واقعی API را اینجا وارد نکن؛ فقط نام env مثل OPENWEATHER_API_KEY.',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('انصراف'),
                ),
                FilledButton.icon(
                  onPressed: () async {
                    final priority = int.tryParse(
                      priorityController.text.trim(),
                    );

                    if (priority == null || priority < 1) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Priority باید عدد مثبت باشد.'),
                        ),
                      );
                      return;
                    }

                    final updated = AdminWeatherProviderConfig(
                      id: config.id,
                      provider: config.provider,
                      isActive: isActive,
                      priority: priority,
                      baseUrl:
                          baseUrlController.text.trim().isEmpty
                              ? null
                              : baseUrlController.text.trim(),
                      apiKeyRef:
                          apiKeyRefController.text.trim().isEmpty
                              ? null
                              : apiKeyRefController.text.trim(),
                      settingsJson: config.settingsJson,
                    );

                    await ref
                        .read(adminWeatherControllerProvider.notifier)
                        .updateProviderConfig(updated);

                    if (context.mounted) Navigator.pop(context);
                  },
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('ذخیره'),
                ),
              ],
            );
          },
        );
      },
    );

    priorityController.dispose();
    baseUrlController.dispose();
    apiKeyRefController.dispose();
  }
}

class _LocationsSection extends ConsumerWidget {
  const _LocationsSection({
    required this.locations,
    required this.selected,
    required this.isSaving,
  });

  final List<AdminWeatherLocation> locations;
  final AdminWeatherLocation? selected;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return _Section(
      title: 'موقعیت‌ها',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (locations.isEmpty)
                const Text('موقعیت آب‌وهوا برای نمایش وجود ندارد.')
              else
                DropdownButtonFormField<AdminWeatherLocation>(
                  initialValue: selected,
                  decoration: const InputDecoration(
                    labelText: 'Weather location',
                    border: OutlineInputBorder(),
                  ),
                  items:
                      locations
                          .map(
                            (location) => DropdownMenuItem(
                              value: location,
                              child: Text(
                                '#${location.id} - ${location.displayName}',
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          )
                          .toList(),
                  onChanged:
                      isSaving
                          ? null
                          : (location) {
                            if (location == null) return;
                            ref
                                .read(adminWeatherControllerProvider.notifier)
                                .selectLocation(location);
                          },
                ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  FilledButton.icon(
                    onPressed:
                        selected == null || isSaving
                            ? null
                            : () => ref
                                .read(adminWeatherControllerProvider.notifier)
                                .refreshSelected(force: true),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Force refresh'),
                  ),
                  OutlinedButton.icon(
                    onPressed:
                        selected == null || isSaving
                            ? null
                            : () => ref
                                .read(adminWeatherControllerProvider.notifier)
                                .refreshSelected(force: false),
                    icon: const Icon(Icons.cached_outlined),
                    label: const Text('Refresh if stale'),
                  ),
                  OutlinedButton.icon(
                    onPressed:
                        selected == null || isSaving
                            ? null
                            : () =>
                                ref
                                    .read(
                                      adminWeatherControllerProvider.notifier,
                                    )
                                    .evaluateSelectedAlerts(),
                    icon: const Icon(Icons.warning_amber_outlined),
                    label: const Text('Evaluate alerts'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CacheStatusSection extends StatelessWidget {
  const _CacheStatusSection({required this.status});

  final AdminWeatherCacheStatus? status;

  @override
  Widget build(BuildContext context) {
    final value = status;

    if (value == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('Cache status موجود نیست.'),
        ),
      );
    }

    return _Section(
      title: 'Cache status',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              Chip(label: Text('Location: ${value.locationId}')),
              Chip(label: Text('Current stale: ${value.currentStale}')),
              Chip(label: Text('Forecast stale: ${value.forecastStale}')),
              Chip(label: Text('Weather stale: ${value.weatherStale}')),
              Chip(label: Text('Current TTL: ${value.currentTtlMinutes}m')),
              Chip(label: Text('Forecast TTL: ${value.forecastTtlMinutes}m')),
            ],
          ),
        ),
      ),
    );
  }
}

class _AlertRulesSection extends ConsumerWidget {
  const _AlertRulesSection({required this.rules, required this.isSaving});

  final List<AdminWeatherAlertRule> rules;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return _Section(
      title: 'قوانین هشدار',
      trailing: FilledButton.icon(
        onPressed:
            isSaving
                ? null
                : () =>
                    ref
                        .read(adminWeatherControllerProvider.notifier)
                        .seedAlertRules(),
        icon: const Icon(Icons.rule_outlined),
        label: const Text('Seed rules'),
      ),
      child:
          rules.isEmpty
              ? const AdminEmptyView(message: 'قانون هشداری وجود ندارد.')
              : AdminDataTable(
                columns: const [
                  DataColumn(label: Text('Type')),
                  DataColumn(label: Text('Severity')),
                  DataColumn(label: Text('Title')),
                  DataColumn(label: Text('Active')),
                ],
                rows:
                    rules.map((rule) {
                      return DataRow(
                        cells: [
                          DataCell(Text(rule.alertType)),
                          DataCell(Text(rule.severity)),
                          DataCell(Text(rule.titleTemplate)),
                          DataCell(Text(rule.isActive ? 'yes' : 'no')),
                        ],
                      );
                    }).toList(),
              ),
    );
  }
}

class _AlertsSection extends StatelessWidget {
  const _AlertsSection({required this.alerts});

  final List<AdminWeatherAlert> alerts;

  @override
  Widget build(BuildContext context) {
    return _Section(
      title: 'هشدارها',
      child:
          alerts.isEmpty
              ? const AdminEmptyView(
                message: 'هشداری برای موقعیت انتخاب‌شده وجود ندارد.',
              )
              : AdminDataTable(
                columns: const [
                  DataColumn(label: Text('ID')),
                  DataColumn(label: Text('Location')),
                  DataColumn(label: Text('Type')),
                  DataColumn(label: Text('Severity')),
                  DataColumn(label: Text('Status')),
                  DataColumn(label: Text('Title')),
                ],
                rows:
                    alerts.map((alert) {
                      return DataRow(
                        cells: [
                          DataCell(Text(alert.id.toString())),
                          DataCell(Text(alert.locationId.toString())),
                          DataCell(Text(alert.alertType)),
                          DataCell(Text(alert.severity)),
                          DataCell(Text(alert.status)),
                          DataCell(Text(alert.title)),
                        ],
                      );
                    }).toList(),
              ),
    );
  }
}

class _EvaluationBox extends StatelessWidget {
  const _EvaluationBox({required this.result});

  final AdminWeatherAlertEvaluation result;

  @override
  Widget build(BuildContext context) {
    return _Section(
      title: 'آخرین ارزیابی هشدارها',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              Chip(label: Text('Location: ${result.locationId}')),
              Chip(label: Text('Rules: ${result.evaluatedRules}')),
              Chip(label: Text('Created: ${result.createdAlerts}')),
              Chip(label: Text('Duplicates: ${result.skippedDuplicates}')),
            ],
          ),
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section({required this.title, required this.child, this.trailing});

  final String title;
  final Widget child;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const Spacer(),
            if (trailing != null) trailing!,
          ],
        ),
        const SizedBox(height: 8),
        child,
      ],
    );
  }
}
