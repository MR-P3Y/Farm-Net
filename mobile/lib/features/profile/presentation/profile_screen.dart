import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/locale_controller.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/theme/theme_controller.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../state/profile_controller.dart';
import 'edit_profile_screen.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(profileControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileControllerProvider);
    final profile = state.profile;

    return Scaffold(
      appBar: AppBar(
        title: const Text('پروفایل من'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return const FarmLoadingView();
          }

          return SingleChildScrollView(
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(r.s(20)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Icon(
                          profile?.profileCompleted == true
                              ? Icons.verified_user_outlined
                              : Icons.info_outline,
                          size: r.s(48),
                        ),
                        SizedBox(height: r.v(12)),
                        Text(
                          profile?.profileCompleted == true
                              ? 'پروفایل شما کامل است'
                              : 'پروفایل شما هنوز کامل نیست',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        SizedBox(height: r.v(20)),
                        _InfoRow(
                          label: 'نام',
                          value: profile?.firstName ?? '-',
                        ),
                        _InfoRow(
                          label: 'نام خانوادگی',
                          value: profile?.lastName ?? '-',
                        ),
                        _InfoRow(
                          label: 'نام نمایشی',
                          value: profile?.displayName ?? '-',
                        ),
                        _InfoRow(
                          label: 'کد ملی',
                          value: profile?.nationalId ?? '-',
                        ),
                        _InfoRow(label: 'آدرس', value: profile?.address ?? '-'),
                        _InfoRow(
                          label: 'کد پستی',
                          value: profile?.postalCode ?? '-',
                        ),
                        if (state.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(24)),
                        FilledButton.icon(
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => const EditProfileScreen(),
                              ),
                            );
                          },
                          icon: const Icon(Icons.edit_outlined),
                          label: const Text('ویرایش پروفایل'),
                        ),
                        SizedBox(height: r.v(12)),
                        OutlinedButton.icon(
                          onPressed: () {
                            context.push('/verifications');
                          },
                          icon: const Icon(Icons.verified_user_outlined),
                          label: const Text('درخواست‌های تأیید من'),
                        ),
                        const Divider(height: 40),
                        Text(
                          'تنظیمات اپلیکیشن',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 12),
                        SwitchListTile(
                          title: const Text('حالت تیره (Dark Mode)'),
                          value: Theme.of(context).brightness == Brightness.dark,
                          onChanged: (_) {
                            ref.read(themeControllerProvider.notifier).toggle();
                          },
                        ),
                        ListTile(
                          title: const Text('زبان (Language)'),
                          subtitle: Text(
                            Localizations.localeOf(context).languageCode == 'fa'
                                ? 'فارسی'
                                : 'English',
                          ),
                          trailing: const Icon(Icons.language),
                          onTap: () {
                            ref.read(localeControllerProvider.notifier).toggle();
                          },
                        ),
                      ],
                    ),
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

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        children: [
          SizedBox(
            width: 130,
            child: Text(label, style: Theme.of(context).textTheme.bodyMedium),
          ),
          Expanded(
            child: Text(value, style: Theme.of(context).textTheme.bodyLarge),
          ),
        ],
      ),
    );
  }
}
