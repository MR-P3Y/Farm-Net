import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/localization/locale_controller.dart';
import '../../../core/theme/theme_controller.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isPersian = Localizations.localeOf(context).languageCode == 'fa';

    return Scaffold(
      appBar: AppBar(title: Text(l10n.settings)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                SwitchListTile(
                  secondary: const Icon(Icons.dark_mode_outlined),
                  title: Text(l10n.darkMode),
                  value: isDark,
                  onChanged: (enabled) {
                    ref
                        .read(themeControllerProvider.notifier)
                        .setThemeMode(
                          enabled ? ThemeMode.dark : ThemeMode.light,
                        );
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.language_rounded),
                  title: Text(l10n.language),
                  subtitle: Text(isPersian ? 'فارسی' : 'English'),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: () {
                    ref.read(localeControllerProvider.notifier).toggle();
                  },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.notifications_outlined),
                  title: Text(
                    l10n.tr(
                      fa: 'تنظیمات اعلان‌ها',
                      en: 'Notification settings',
                    ),
                  ),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: () => context.push('/notifications/preferences'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
