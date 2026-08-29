import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';
import 'auth_page_shell.dart';
import 'otp_verify_screen.dart';

class OtpRequestScreen extends ConsumerStatefulWidget {
  const OtpRequestScreen({super.key});

  @override
  ConsumerState<OtpRequestScreen> createState() => _OtpRequestScreenState();
}

class _OtpRequestScreenState extends ConsumerState<OtpRequestScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    FocusManager.instance.primaryFocus?.unfocus();
    final phone = _phoneController.text.trim();
    final ok = await ref
        .read(authControllerProvider.notifier)
        .requestOtp(phone: phone);
    if (!ok || !mounted) return;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => OtpVerifyScreen(phone: phone)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    final l10n = context.l10n;

    return AuthPageShell(
      maxWidth: 400,
      desktopAlignment: AlignmentDirectional.centerStart,
      child: FarmGlassCard(
        key: const Key('otp-request-card'),
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
                Icons.phone_android_rounded,
                color: Colors.white,
                size: 48,
              ),
              const SizedBox(height: 14),
              Text(
                l10n.loginWithMobile,
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
                  fa: 'شماره موبایل خود را وارد کنید تا کد ورود ارسال شود.',
                  en: 'Enter your mobile number to receive a sign-in code.',
                ),
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
              const SizedBox(height: 24),
              Theme(
                data: _inputTheme(context),
                child: FarmTextField(
                  key: const Key('otp-phone'),
                  controller: _phoneController,
                  label: l10n.mobileNumber,
                  keyboardType: TextInputType.phone,
                  textInputAction: TextInputAction.done,
                  prefixIcon: Icons.phone_iphone_rounded,
                  autofillHints: const [AutofillHints.telephoneNumber],
                  validator: (value) => _validatePhone(l10n, value),
                ),
              ),
              if (auth.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  l10n.tr(
                    fa: 'ارسال کد انجام نشد. شماره و اتصال را بررسی کنید.',
                    en:
                        'Could not send the code. Check the number and connection.',
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
                key: const Key('otp-request-action'),
                label: l10n.getOtpCode,
                icon: Icons.sms_outlined,
                isLoading: auth.isLoading,
                onPressed: auth.isLoading ? null : _requestOtp,
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

  String? _validatePhone(AppLocalizations l10n, String? value) {
    final digits = (value ?? '').replaceAll(RegExp(r'[^0-9۰-۹٠-٩]'), '');
    if (digits.length < 10 || digits.length > 14) {
      return l10n.tr(
        fa: 'شماره موبایل معتبر وارد کنید',
        en: 'Enter a valid mobile number',
      );
    }
    return null;
  }
}
