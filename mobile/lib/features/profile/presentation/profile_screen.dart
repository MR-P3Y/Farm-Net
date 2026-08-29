import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_error_view.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../auth/data/auth_models.dart';
import '../../auth/state/auth_controller.dart';
import '../../geo/data/geo_models.dart';
import '../data/profile_models.dart';
import '../state/profile_controller.dart';
import '../state/profile_state.dart';

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
    Future.microtask(() => ref.read(profileControllerProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileControllerProvider);
    final auth = ref.watch(authControllerProvider);
    final l10n = context.l10n;

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.tr(fa: 'پروفایل من', en: 'My profile'),
        showBack: false,
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) return const FarmLoadingView();
          if (state.profile == null && state.errorMessage != null) {
            return FarmErrorView(
              message: l10n.tr(
                fa: 'دریافت اطلاعات پروفایل انجام نشد.',
                en: 'Could not load your profile.',
              ),
              onRetry:
                  () => ref.read(profileControllerProvider.notifier).load(),
            );
          }

          final profile = state.profile;
          if (profile == null) {
            return FarmErrorView(
              message: l10n.tr(
                fa: 'اطلاعات پروفایل در دسترس نیست.',
                en: 'Profile information is unavailable.',
              ),
              onRetry:
                  () => ref.read(profileControllerProvider.notifier).load(),
            );
          }

          return RefreshIndicator(
            onRefresh:
                () => ref.read(profileControllerProvider.notifier).load(),
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: r.pagePadding().copyWith(bottom: r.v(28)),
              children: [
                Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 820),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _ProfileHeader(
                          profile: profile,
                          user: auth.user,
                          onEdit: () => context.push('/profile/edit'),
                        ),
                        if (state.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          _InlineNotice(
                            message: l10n.tr(
                              fa:
                                  'بخشی از اطلاعات مکانی به‌روز نشد. برای تلاش دوباره صفحه را تازه کنید.',
                              en:
                                  'Some location information was not refreshed. Pull down to retry.',
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(14)),
                        _AccountCard(user: auth.user),
                        SizedBox(height: r.v(14)),
                        _PersonalInfoCard(profile: profile, state: state),
                        SizedBox(height: r.v(14)),
                        _ShortcutCard(
                          onVerification: () => context.push('/verifications'),
                          onFavorites: () => context.push('/favorites'),
                          onSecurity: () => context.push('/profile/security'),
                          onSettings: () => context.push('/settings'),
                        ),
                        SizedBox(height: r.v(18)),
                        FarmButton(
                          label: l10n.logout,
                          icon: Icons.logout_rounded,
                          variant: FarmButtonVariant.destructive,
                          expand: true,
                          onPressed: auth.isLoading ? null : _confirmLogout,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _confirmLogout() async {
    final l10n = context.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (dialogContext) => AlertDialog(
            title: Text(l10n.logout),
            content: Text(
              l10n.tr(
                fa: 'آیا می‌خواهید از این حساب خارج شوید؟',
                en: 'Do you want to log out of this account?',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: Text(l10n.logout),
              ),
            ],
          ),
    );
    if (confirmed != true || !mounted) return;

    ref.read(profileControllerProvider.notifier).reset();
    await ref.read(authControllerProvider.notifier).logout();
    if (mounted) context.go('/');
  }
}

class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({
    required this.profile,
    required this.user,
    required this.onEdit,
  });

  final UserProfile profile;
  final AuthUser? user;
  final VoidCallback onEdit;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final colors = Theme.of(context).colorScheme;
    final fullName = [
      profile.firstName,
      profile.lastName,
    ].whereType<String>().where((item) => item.trim().isNotEmpty).join(' ');
    final title =
        profile.displayName?.trim().isNotEmpty == true
            ? profile.displayName!.trim()
            : fullName.isNotEmpty
            ? fullName
            : user?.email ??
                user?.phone ??
                l10n.tr(fa: 'کاربر فارم‌نت', en: 'Farm Net user');
    final completed = _completedProfileFields(profile);
    const requiredFields = 6;
    final progress = completed / requiredFields;
    final avatarUrl = absoluteApiUrl(profile.avatarUrl);

    return FarmGlassCard(
      padding: const EdgeInsets.all(18),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: colors.primaryContainer,
                foregroundColor: colors.onPrimaryContainer,
                backgroundImage:
                    avatarUrl == null ? null : NetworkImage(avatarUrl),
                child:
                    avatarUrl == null
                        ? const Icon(Icons.person_rounded, size: 34)
                        : null,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 4),
                    Text(
                      profile.profileCompleted
                          ? l10n.tr(
                            fa: 'آماده برای تأیید هویت',
                            en: 'Ready for identity verification',
                          )
                          : l10n.tr(
                            fa:
                                '$completed از $requiredFields مورد ضروری تکمیل شده',
                            en:
                                '$completed of $requiredFields required items completed',
                          ),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              IconButton.filledTonal(
                tooltip: l10n.tr(fa: 'ویرایش پروفایل', en: 'Edit profile'),
                onPressed: onEdit,
                icon: const Icon(Icons.edit_outlined),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(99),
            child: LinearProgressIndicator(value: progress, minHeight: 7),
          ),
        ],
      ),
    );
  }
}

class _AccountCard extends StatelessWidget {
  const _AccountCard({required this.user});

  final AuthUser? user;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return _SectionCard(
      title: l10n.tr(fa: 'حساب کاربری', en: 'Account'),
      icon: Icons.shield_outlined,
      children: [
        if (user?.email != null)
          _AccountIdentityRow(
            icon: Icons.alternate_email_rounded,
            label: l10n.tr(fa: 'ایمیل', en: 'Email'),
            value: user!.email!,
            verified: user!.isEmailVerified,
          ),
        if (user?.phone != null)
          _AccountIdentityRow(
            icon: Icons.phone_outlined,
            label: l10n.tr(fa: 'موبایل', en: 'Mobile'),
            value: user!.phone!,
            verified: user!.isPhoneVerified,
          ),
        if (user?.email == null && user?.phone == null)
          Text(
            l10n.tr(
              fa: 'اطلاعات ورود حساب در دسترس نیست.',
              en: 'Account sign-in information is unavailable.',
            ),
          ),
      ],
    );
  }
}

class _AccountIdentityRow extends StatelessWidget {
  const _AccountIdentityRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.verified,
  });

  final IconData icon;
  final String label;
  final String value;
  final bool verified;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon),
      title: Text(label),
      subtitle: Text(value, textDirection: TextDirection.ltr),
      trailing: Chip(
        avatar: Icon(
          verified ? Icons.verified_rounded : Icons.info_outline_rounded,
          size: 17,
        ),
        label: Text(
          verified
              ? l10n.tr(fa: 'تأییدشده', en: 'Verified')
              : l10n.tr(fa: 'تأییدنشده', en: 'Not verified'),
        ),
        visualDensity: VisualDensity.compact,
      ),
    );
  }
}

class _PersonalInfoCard extends StatelessWidget {
  const _PersonalInfoCard({required this.profile, required this.state});

  final UserProfile profile;
  final ProfileState state;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final province = _provinceName(state.provinces, profile.provinceId);
    final county = _countyName(state.counties, profile.countyId);
    final city = _cityName(state.cities, profile.cityId);
    final location = [
      province,
      county,
      city,
    ].whereType<String>().where((value) => value.isNotEmpty).join('، ');

    return _SectionCard(
      title: l10n.tr(fa: 'اطلاعات شخصی', en: 'Personal details'),
      icon: Icons.badge_outlined,
      children: [
        _InfoRow(
          label: l10n.tr(fa: 'نام', en: 'Name'),
          value: _fullName(profile),
        ),
        _InfoRow(
          label: l10n.tr(fa: 'نام نمایشی', en: 'Display name'),
          value: profile.displayName,
        ),
        _InfoRow(
          label: l10n.tr(fa: 'کد ملی', en: 'National ID'),
          value: _maskedNationalId(context, profile.nationalId),
        ),
        _InfoRow(
          label: l10n.tr(fa: 'تاریخ تولد', en: 'Date of birth'),
          value: formatApiDate(context, profile.birthDate),
        ),
        _InfoRow(
          label: l10n.tr(fa: 'جنسیت', en: 'Gender'),
          value: _genderLabel(context, profile.gender),
        ),
        _InfoRow(label: l10n.tr(fa: 'موقعیت', en: 'Location'), value: location),
        _InfoRow(
          label: l10n.tr(fa: 'آدرس', en: 'Address'),
          value: profile.address,
        ),
        _InfoRow(
          label: l10n.tr(fa: 'کد پستی', en: 'Postal code'),
          value: profile.postalCode,
        ),
        if (profile.bio?.trim().isNotEmpty == true)
          _InfoRow(
            label: l10n.tr(fa: 'درباره من', en: 'About me'),
            value: profile.bio,
          ),
      ],
    );
  }
}

class _ShortcutCard extends StatelessWidget {
  const _ShortcutCard({
    required this.onVerification,
    required this.onFavorites,
    required this.onSecurity,
    required this.onSettings,
  });

  final VoidCallback onVerification;
  final VoidCallback onFavorites;
  final VoidCallback onSecurity;
  final VoidCallback onSettings;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return _SectionCard(
      title: l10n.tr(fa: 'مدیریت حساب', en: 'Account management'),
      icon: Icons.tune_rounded,
      children: [
        _ShortcutTile(
          icon: Icons.verified_user_outlined,
          title: l10n.tr(
            fa: 'تأیید هویت و مدارک',
            en: 'Identity and documents',
          ),
          onTap: onVerification,
        ),
        _ShortcutTile(
          icon: Icons.favorite_border_rounded,
          title: l10n.tr(fa: 'علاقه‌مندی‌های من', en: 'My favorites'),
          onTap: onFavorites,
        ),
        _ShortcutTile(
          icon: Icons.security_rounded,
          title: l10n.tr(fa: 'امنیت حساب', en: 'Account security'),
          onTap: onSecurity,
        ),
        _ShortcutTile(
          icon: Icons.settings_outlined,
          title: l10n.settings,
          onTap: onSettings,
        ),
      ],
    );
  }
}

class _ShortcutTile extends StatelessWidget {
  const _ShortcutTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(icon),
      title: Text(title),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: onTap,
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.title,
    required this.icon,
    required this.children,
  });

  final String title;
  final IconData icon;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(icon, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String? value;

  @override
  Widget build(BuildContext context) {
    final visibleValue = value?.trim().isNotEmpty == true ? value!.trim() : '-';
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 125,
            child: Text(label, style: Theme.of(context).textTheme.bodySmall),
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(visibleValue)),
        ],
      ),
    );
  }
}

class _InlineNotice extends StatelessWidget {
  const _InlineNotice({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Material(
      color: colors.errorContainer,
      borderRadius: BorderRadius.circular(14),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Icon(Icons.info_outline_rounded, color: colors.onErrorContainer),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                message,
                style: TextStyle(color: colors.onErrorContainer),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

int _completedProfileFields(UserProfile profile) {
  return [
        profile.firstName,
        profile.lastName,
        profile.nationalId,
        profile.provinceId,
        profile.countyId,
        profile.address,
      ]
      .where((value) => value != null && value.toString().trim().isNotEmpty)
      .length;
}

String _fullName(UserProfile profile) {
  return [
    profile.firstName,
    profile.lastName,
  ].whereType<String>().where((item) => item.trim().isNotEmpty).join(' ');
}

String? _provinceName(List<GeoProvince> items, int? id) {
  if (id == null) return null;
  for (final item in items) {
    if (item.id == id) return item.name;
  }
  return null;
}

String? _countyName(List<GeoCounty> items, int? id) {
  if (id == null) return null;
  for (final item in items) {
    if (item.id == id) return item.name;
  }
  return null;
}

String? _cityName(List<GeoCity> items, int? id) {
  if (id == null) return null;
  for (final item in items) {
    if (item.id == id) return item.name;
  }
  return null;
}

String _maskedNationalId(BuildContext context, String? value) {
  final normalized = toEnglishDigits(value?.trim());
  if (normalized.length < 4) return '-';
  final masked = '••••••${normalized.substring(normalized.length - 4)}';
  return context.l10n.isFa ? toPersianDigits(masked) : masked;
}

String _genderLabel(BuildContext context, String? value) {
  final l10n = context.l10n;
  return switch (value) {
    'male' => l10n.tr(fa: 'مرد', en: 'Male'),
    'female' => l10n.tr(fa: 'زن', en: 'Female'),
    'other' => l10n.tr(fa: 'سایر', en: 'Other'),
    _ => '-',
  };
}
