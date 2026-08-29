import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';
import 'auth_page_shell.dart';

class OtpVerifyScreen extends ConsumerStatefulWidget {
  const OtpVerifyScreen({super.key, required this.phone});

  final String phone;

  @override
  ConsumerState<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends ConsumerState<OtpVerifyScreen> {
  final _formKey = GlobalKey<FormState>();
  final _codeController = TextEditingController();

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _verifyOtp() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    FocusManager.instance.primaryFocus?.unfocus();
    final ok = await ref
        .read(authControllerProvider.notifier)
        .verifyOtp(phone: widget.phone, code: _codeController.text.trim());
    if (!ok || !mounted) return;
    Navigator.of(context).popUntil((route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    final l10n = context.l10n;

    return AuthPageShell(
      maxWidth: 400,
      desktopAlignment: AlignmentDirectional.centerStart,
      child: FarmGlassCard(
        key: const Key('otp-verify-card'),
        borderRadius: 28,
        opacity: .1,
        blur: 16,
        padding: const EdgeInsetsDirectional.fromSTEB(24, 12, 24, 28),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Align(
                alignment: AlignmentDirectional.centerStart,
                child: FarmBackButton(
                  color: Colors.white,
                  fallbackLocation: '/login',
                ),
              ),
              const Icon(
                Icons.mark_email_read_rounded,
                color: Colors.white,
                size: 48,
              ),
              const SizedBox(height: 14),
              Text(
                l10n.verifyCode,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                l10n.tr(
                  fa: 'کد ارسال‌شده برای ${widget.phone} را وارد کنید.',
                  en: 'Enter the code sent to ${widget.phone}.',
                ),
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
              if (auth.devOtpCode != null) ...[
                const SizedBox(height: 12),
                Container(
                  key: const Key('otp-dev-code'),
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: .08),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    l10n.tr(
                      fa: 'کد محیط توسعه: ${auth.devOtpCode}',
                      en: 'Development code: ${auth.devOtpCode}',
                    ),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.white70),
                  ),
                ),
              ],
              const SizedBox(height: 22),
              Theme(
                data: _inputTheme(context),
                child: FarmTextField(
                  key: const Key('otp-code'),
                  controller: _codeController,
                  label: l10n.verificationCode,
                  keyboardType: TextInputType.number,
                  textInputAction: TextInputAction.done,
                  prefixIcon: Icons.pin_outlined,
                  autofillHints: const [AutofillHints.oneTimeCode],
                  validator:
                      (value) =>
                          value == null || value.trim().length < 4
                              ? l10n.tr(
                                fa: 'کد ورود را کامل وارد کنید',
                                en: 'Enter the complete sign-in code',
                              )
                              : null,
                ),
              ),
              if (auth.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  l10n.tr(
                    fa: 'کد صحیح نیست یا زمان آن تمام شده است.',
                    en: 'The code is invalid or has expired.',
                  ),
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFFFFB4AB),
                    fontSize: 12,
                  ),
                ),
              ],
              const SizedBox(height: 24),
              FarmButton(
                key: const Key('otp-verify-action'),
                label: l10n.verifyAndLogin,
                icon: Icons.login_rounded,
                isLoading: auth.isLoading,
                onPressed: auth.isLoading ? null : _verifyOtp,
              ),
            ],
          ),
        ),
      ),
    );
  }

  ThemeData _inputTheme(BuildContext context) {
    return Theme.of(context).copyWith(
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withValues(alpha: .06),
        labelStyle: const TextStyle(color: Colors.white70),
        prefixIconColor: Colors.white70,
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: .18)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.white),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.redAccent),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.redAccent),
        ),
        errorStyle: const TextStyle(color: Color(0xFFFFB4AB)),
      ),
    );
  }
}
