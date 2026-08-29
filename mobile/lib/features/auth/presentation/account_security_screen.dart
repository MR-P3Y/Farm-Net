import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_error_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_primary_action_bar.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../data/auth_models.dart';
import '../state/account_security_controller.dart';
import '../state/auth_controller.dart';

class AccountSecurityScreen extends ConsumerStatefulWidget {
  const AccountSecurityScreen({super.key});

  @override
  ConsumerState<AccountSecurityScreen> createState() =>
      _AccountSecurityScreenState();
}

class _AccountSecurityScreenState extends ConsumerState<AccountSecurityScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(accountSecurityControllerProvider.notifier).load(),
    );
  }

  @override
  void dispose() {
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(accountSecurityControllerProvider);
    final user = ref.watch(authControllerProvider).user;
    final l10n = context.l10n;
    final canChangePassword = user?.email?.isNotEmpty == true;

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.tr(fa: 'امنیت حساب', en: 'Account security'),
        fallbackLocation: '/profile',
      ),
      bottomNavigationBar:
          canChangePassword
              ? FarmPrimaryActionBar(
                label: l10n.tr(fa: 'تغییر رمز عبور', en: 'Change password'),
                loadingLabel: l10n.tr(
                  fa: 'در حال تغییر رمز…',
                  en: 'Changing password…',
                ),
                icon: Icons.password_rounded,
                isLoading: state.isSaving,
                onPressed: _changePassword,
              )
              : null,
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading && state.sessions.isEmpty) {
            return const FarmLoadingView();
          }
          if (state.errorCode != null && state.sessions.isEmpty) {
            return FarmErrorView(
              message: _errorMessage(state.errorCode!),
              onRetry:
                  () =>
                      ref
                          .read(accountSecurityControllerProvider.notifier)
                          .load(),
            );
          }

          return RefreshIndicator(
            onRefresh:
                () =>
                    ref.read(accountSecurityControllerProvider.notifier).load(),
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: r.pagePadding().copyWith(bottom: r.v(28)),
              children: [
                Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 760),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _SecurityIntro(),
                        SizedBox(height: r.v(14)),
                        if (canChangePassword)
                          _PasswordCard(
                            formKey: _formKey,
                            currentPasswordController:
                                _currentPasswordController,
                            newPasswordController: _newPasswordController,
                            confirmPasswordController:
                                _confirmPasswordController,
                          )
                        else
                          _PhoneOnlyNotice(),
                        SizedBox(height: r.v(14)),
                        _SessionsCard(
                          sessions: state.sessions,
                          isSaving: state.isSaving,
                          onRevoke: _confirmRevoke,
                          onRevokeOthers: _confirmRevokeOthers,
                        ),
                        if (state.errorCode != null) ...[
                          SizedBox(height: r.v(14)),
                          _ErrorNotice(
                            message: _errorMessage(state.errorCode!),
                          ),
                        ],
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

  Future<void> _changePassword() async {
    if (_formKey.currentState?.validate() != true) return;
    final revoked = await ref
        .read(accountSecurityControllerProvider.notifier)
        .changePassword(
          currentPassword: _currentPasswordController.text,
          newPassword: _newPasswordController.text,
        );
    if (revoked == null || !mounted) return;

    _currentPasswordController.clear();
    _newPasswordController.clear();
    _confirmPasswordController.clear();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          context.l10n.tr(
            fa: 'رمز عبور تغییر کرد و نشست‌های دیگر بسته شدند.',
            en: 'Password changed and other sessions were closed.',
          ),
        ),
      ),
    );
  }

  Future<void> _confirmRevoke(AuthSessionModel session) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (dialogContext) => AlertDialog(
            title: Text(context.l10n.tr(fa: 'بستن نشست', en: 'Close session')),
            content: Text(
              context.l10n.tr(
                fa: 'دسترسی این دستگاه بلافاصله لغو شود؟',
                en: 'Revoke access for this device immediately?',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: Text(context.l10n.tr(fa: 'بستن', en: 'Close')),
              ),
            ],
          ),
    );
    if (confirmed != true || !mounted) return;
    final ok = await ref
        .read(accountSecurityControllerProvider.notifier)
        .revokeSession(session.id);
    if (!ok || !mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          context.l10n.tr(fa: 'نشست بسته شد.', en: 'Session closed.'),
        ),
      ),
    );
  }

  Future<void> _confirmRevokeOthers() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (dialogContext) => AlertDialog(
            title: Text(
              context.l10n.tr(
                fa: 'بستن همه نشست‌های دیگر',
                en: 'Close all other sessions',
              ),
            ),
            content: Text(
              context.l10n.tr(
                fa:
                    'این دستگاه متصل می‌ماند و دسترسی همه دستگاه‌های دیگر لغو می‌شود.',
                en:
                    'This device stays signed in and every other device is revoked.',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: Text(context.l10n.tr(fa: 'تأیید', en: 'Confirm')),
              ),
            ],
          ),
    );
    if (confirmed != true || !mounted) return;
    final count =
        await ref
            .read(accountSecurityControllerProvider.notifier)
            .revokeOtherSessions();
    if (count == null || !mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          context.l10n.tr(
            fa: '$count نشست دیگر بسته شد.',
            en: '$count other sessions closed.',
          ),
        ),
      ),
    );
  }

  String _errorMessage(String code) {
    if (code == 'AUTH_CURRENT_PASSWORD_INVALID') {
      return context.l10n.tr(
        fa: 'رمز عبور فعلی صحیح نیست.',
        en: 'The current password is incorrect.',
      );
    }
    if (code == 'VALIDATION_ERROR') {
      return context.l10n.tr(
        fa: 'اطلاعات واردشده معتبر نیست.',
        en: 'The entered information is invalid.',
      );
    }
    return context.l10n.tr(
      fa: 'عملیات امنیت حساب انجام نشد. دوباره تلاش کنید.',
      en: 'The account security operation failed. Try again.',
    );
  }
}

class _SecurityIntro extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Card(
      color: colors.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            Icon(
              Icons.shield_outlined,
              size: 34,
              color: colors.onPrimaryContainer,
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Text(
                context.l10n.tr(
                  fa:
                      'رمز عبور و دستگاه‌های متصل به حساب را از این بخش مدیریت کنید.',
                  en:
                      'Manage your password and devices signed in to this account.',
                ),
                style: TextStyle(color: colors.onPrimaryContainer),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PasswordCard extends StatelessWidget {
  const _PasswordCard({
    required this.formKey,
    required this.currentPasswordController,
    required this.newPasswordController,
    required this.confirmPasswordController,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController currentPasswordController;
  final TextEditingController newPasswordController;
  final TextEditingController confirmPasswordController;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Form(
          key: formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                l10n.tr(fa: 'تغییر رمز عبور', en: 'Change password'),
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 16),
              FarmTextField(
                controller: currentPasswordController,
                label: l10n.tr(fa: 'رمز عبور فعلی', en: 'Current password'),
                obscureText: true,
                prefixIcon: Icons.lock_outline_rounded,
                validator:
                    (value) =>
                        value == null || value.isEmpty
                            ? l10n.tr(
                              fa: 'رمز عبور فعلی را وارد کنید',
                              en: 'Enter the current password',
                            )
                            : null,
              ),
              const SizedBox(height: 12),
              FarmTextField(
                controller: newPasswordController,
                label: l10n.tr(fa: 'رمز عبور جدید', en: 'New password'),
                obscureText: true,
                prefixIcon: Icons.password_rounded,
                validator:
                    (value) =>
                        value == null || value.length < 8
                            ? l10n.tr(
                              fa: 'رمز جدید باید حداقل ۸ نویسه باشد',
                              en: 'New password must be at least 8 characters',
                            )
                            : null,
              ),
              const SizedBox(height: 12),
              FarmTextField(
                controller: confirmPasswordController,
                label: l10n.tr(
                  fa: 'تکرار رمز جدید',
                  en: 'Confirm new password',
                ),
                obscureText: true,
                prefixIcon: Icons.password_rounded,
                validator:
                    (value) =>
                        value != newPasswordController.text
                            ? l10n.tr(
                              fa: 'تکرار رمز عبور یکسان نیست',
                              en: 'Passwords do not match',
                            )
                            : null,
              ),
              const SizedBox(height: 10),
              Text(
                l10n.tr(
                  fa:
                      'پس از تغییر رمز، همه دستگاه‌های دیگر از حساب خارج می‌شوند.',
                  en: 'Changing the password signs out every other device.',
                ),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PhoneOnlyNotice extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Text(
          context.l10n.tr(
            fa:
                'این حساب با موبایل و رمز یک‌بارمصرف وارد شده است؛ رمز ثابت برای آن فعال نیست.',
            en:
                'This account signs in with mobile OTP and has no fixed password.',
          ),
        ),
      ),
    );
  }
}

class _SessionsCard extends StatelessWidget {
  const _SessionsCard({
    required this.sessions,
    required this.isSaving,
    required this.onRevoke,
    required this.onRevokeOthers,
  });

  final List<AuthSessionModel> sessions;
  final bool isSaving;
  final ValueChanged<AuthSessionModel> onRevoke;
  final VoidCallback onRevokeOthers;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final otherCount = sessions.where((session) => !session.isCurrent).length;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              l10n.tr(fa: 'نشست‌های فعال', en: 'Active sessions'),
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            if (sessions.isEmpty)
              Text(
                l10n.tr(
                  fa: 'نشست فعالی نمایش داده نشد.',
                  en: 'No active session was returned.',
                ),
              )
            else
              for (final session in sessions)
                _SessionTile(
                  session: session,
                  onRevoke:
                      session.isCurrent || isSaving
                          ? null
                          : () => onRevoke(session),
                ),
            if (otherCount > 0) ...[
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: isSaving ? null : onRevokeOthers,
                icon: const Icon(Icons.phonelink_erase_rounded),
                label: Text(
                  l10n.tr(
                    fa: 'بستن همه نشست‌های دیگر',
                    en: 'Close all other sessions',
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _SessionTile extends StatelessWidget {
  const _SessionTile({required this.session, required this.onRevoke});

  final AuthSessionModel session;
  final VoidCallback? onRevoke;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final device = _deviceLabel(context, session.userAgent);
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(_deviceIcon(session.userAgent)),
      title: Text(device),
      subtitle: Text(
        [
          if (session.ipAddress?.isNotEmpty == true) session.ipAddress!,
          l10n.tr(
            fa:
                'آخرین فعالیت: ${formatApiDate(context, session.lastSeenAt, showTime: true)}',
            en:
                'Last active: ${formatApiDate(context, session.lastSeenAt, showTime: true)}',
          ),
        ].join('\n'),
      ),
      isThreeLine: session.ipAddress?.isNotEmpty == true,
      trailing:
          session.isCurrent
              ? Chip(
                label: Text(l10n.tr(fa: 'این دستگاه', en: 'This device')),
                visualDensity: VisualDensity.compact,
              )
              : IconButton(
                tooltip: l10n.tr(fa: 'بستن نشست', en: 'Close session'),
                onPressed: onRevoke,
                icon: const Icon(Icons.logout_rounded),
              ),
    );
  }
}

class _ErrorNotice extends StatelessWidget {
  const _ErrorNotice({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Material(
      color: colors.errorContainer,
      borderRadius: BorderRadius.circular(14),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Text(message, style: TextStyle(color: colors.onErrorContainer)),
      ),
    );
  }
}

String _deviceLabel(BuildContext context, String? userAgent) {
  final value = userAgent?.toLowerCase() ?? '';
  if (value.contains('android')) return 'Android';
  if (value.contains('iphone') || value.contains('ios')) return 'iPhone';
  if (value.contains('edg/')) return 'Microsoft Edge';
  if (value.contains('chrome')) return 'Chrome';
  if (value.contains('firefox')) return 'Firefox';
  return context.l10n.tr(fa: 'دستگاه ناشناس', en: 'Unknown device');
}

IconData _deviceIcon(String? userAgent) {
  final value = userAgent?.toLowerCase() ?? '';
  if (value.contains('android') ||
      value.contains('iphone') ||
      value.contains('ios')) {
    return Icons.smartphone_rounded;
  }
  return Icons.computer_rounded;
}
