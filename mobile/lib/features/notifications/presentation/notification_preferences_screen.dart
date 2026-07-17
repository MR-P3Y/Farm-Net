import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/notification_api.dart';
import '../data/notification_repository.dart';

class NotificationPreferencesScreen extends ConsumerStatefulWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  ConsumerState<NotificationPreferencesScreen> createState() =>
      _NotificationPreferencesScreenState();
}

class _NotificationPreferencesScreenState
    extends ConsumerState<NotificationPreferencesScreen> {
  bool _loading = true;
  String? _error;
  Map<String, bool> _values = const {};

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    try {
      final rows =
          await ref.read(notificationRepositoryProvider).listPreferences();
      final values = <String, bool>{
        'in_app': true,
        'email': false,
        'sms': false,
        'push': false,
      };
      for (final row in rows.where((item) => item.eventType == '*')) {
        values[row.channel] = row.isEnabled;
      }
      if (mounted) {
        setState(() {
          _values = values;
          _loading = false;
          _error = null;
        });
      }
    } on NotificationApiException catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.error.message;
        });
      }
    }
  }

  Future<void> _set(String channel, bool enabled) async {
    final previous = _values[channel] ?? false;
    setState(() => _values = {..._values, channel: enabled});
    try {
      await ref
          .read(notificationRepositoryProvider)
          .setPreference(channel: channel, isEnabled: enabled);
    } on NotificationApiException catch (e) {
      if (mounted) {
        setState(() {
          _values = {..._values, channel: previous};
          _error = e.error.message;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    const labels = {
      'in_app': 'اعلان درون‌برنامه‌ای',
      'email': 'ایمیل',
      'sms': 'پیامک',
      'push': 'Push',
    };
    return Scaffold(
      appBar: AppBar(title: const Text('تنظیمات اعلان‌ها')),
      body:
          _loading
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_error != null)
                    Text(
                      _error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  for (final entry in labels.entries)
                    SwitchListTile(
                      title: Text(entry.value),
                      subtitle:
                          entry.key == 'push'
                              ? const Text(
                                'نیازمند اتصال توکن دستگاه به سرویس Push',
                              )
                              : null,
                      value: _values[entry.key] ?? false,
                      onChanged: (value) => _set(entry.key, value),
                    ),
                ],
              ),
    );
  }
}
