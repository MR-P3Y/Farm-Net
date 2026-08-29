import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../data/auth_api.dart';
import '../data/auth_repository.dart';
import 'auth_page_shell.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _requestFormKey = GlobalKey<FormState>();
  final _confirmFormKey = GlobalKey<FormState>();
  final _identifierController = TextEditingController();
  final _codeController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  int _step = 0;
  bool _isLoading = false;
  bool _passwordVisible = false;
  bool _confirmPasswordVisible = false;
  String? _devCode;
  String? _errorCode;
  String? _errorMessage;

  @override
  void dispose() {
    _identifierController.dispose();
    _codeController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _requestCode({bool validate = true}) async {
    if (validate && !(_requestFormKey.currentState?.validate() ?? false)) {
      return;
    }
    setState(() {
      _isLoading = true;
      _errorCode = null;
      _errorMessage = null;
      _devCode = null;
    });
    try {
      final result = await ref
          .read(authRepositoryProvider)
          .requestPasswordReset(identifier: _identifierController.text.trim());
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _devCode = result.devCode;
        _step = 1;
      });
    } on AuthApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorCode = error.error.code;
        _errorMessage = error.error.message;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorCode = 'NETWORK_ERROR';
      });
    }
  }

  Future<void> _confirmReset() async {
    if (!(_confirmFormKey.currentState?.validate() ?? false)) return;
    setState(() {
      _isLoading = true;
      _errorCode = null;
      _errorMessage = null;
    });
    try {
      await ref
          .read(authRepositoryProvider)
          .confirmPasswordReset(
            identifier: _identifierController.text.trim(),
            code: _codeController.text.trim(),
            newPassword: _passwordController.text,
          );
      if (!mounted) return;
      FocusManager.instance.primaryFocus?.unfocus();
      setState(() {
        _isLoading = false;
        _step = 2;
      });
    } on AuthApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorCode = error.error.code;
        _errorMessage = error.error.message;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorCode = 'NETWORK_ERROR';
      });
    }
  }

  void _back() {
    FocusManager.instance.primaryFocus?.unfocus();
    if (_step == 1) {
      setState(() {
        _step = 0;
        _errorCode = null;
        _errorMessage = null;
      });
      return;
    }
    if (context.canPop()) {
      context.pop();
    } else {
      context.go('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return PopScope(
      canPop: _step != 1,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _back();
      },
      child: AuthPageShell(
        maxWidth: 400,
        child: FarmGlassCard(
          key: const Key('forgot-password-card'),
          borderRadius: 28,
          opacity: .1,
          blur: 16,
          padding: const EdgeInsetsDirectional.fromSTEB(24, 12, 24, 28),
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 220),
            child: switch (_step) {
              0 => _requestStep(l10n),
              1 => _confirmStep(l10n),
              _ => _successStep(l10n),
            },
          ),
        ),
      ),
    );
  }

  Widget _requestStep(AppLocalizations l10n) {
    return Form(
      key: _requestFormKey,
      child: Column(
        key: const ValueKey('password-reset-request-step'),
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: FarmBackButton(
              color: Colors.white,
              fallbackLocation: '/login',
              onPressed: _back,
            ),
          ),
          const Icon(Icons.lock_reset_rounded, color: Colors.white, size: 48),
          const SizedBox(height: 12),
          Text(
            l10n.tr(fa: 'بازیابی رمز عبور', en: 'Reset password'),
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 21,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            l10n.tr(
              fa: 'ایمیل یا شماره موبایل متصل به حساب را وارد کنید.',
              en: 'Enter the email or mobile number linked to your account.',
            ),
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white70, fontSize: 13),
          ),
          const SizedBox(height: 24),
          _AuthInputTheme(
            child: FarmTextField(
              key: const Key('password-reset-identifier'),
              controller: _identifierController,
              label: l10n.tr(
                fa: 'ایمیل یا شماره موبایل',
                en: 'Email or mobile number',
              ),
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.done,
              prefixIcon: Icons.alternate_email_rounded,
              validator: (value) => _validateIdentifier(l10n, value),
            ),
          ),
          if (_errorCode != null) _errorPanel(l10n),
          const SizedBox(height: 24),
          FarmButton(
            key: const Key('password-reset-request-action'),
            label: l10n.tr(fa: 'دریافت کد بازیابی', en: 'Get reset code'),
            icon: Icons.mark_email_unread_outlined,
            isLoading: _isLoading,
            onPressed: _isLoading ? null : _requestCode,
          ),
        ],
      ),
    );
  }

  Widget _confirmStep(AppLocalizations l10n) {
    return Form(
      key: _confirmFormKey,
      child: Column(
        key: const ValueKey('password-reset-confirm-step'),
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: FarmBackButton(
              color: Colors.white,
              fallbackLocation: '/login',
              onPressed: _back,
            ),
          ),
          const Icon(
            Icons.verified_user_outlined,
            color: Colors.white,
            size: 48,
          ),
          const SizedBox(height: 12),
          Text(
            l10n.tr(fa: 'کد و رمز جدید', en: 'Code and new password'),
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 21,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            l10n.tr(
              fa: 'کد ارسال‌شده را همراه رمز جدید وارد کنید.',
              en: 'Enter the received code and your new password.',
            ),
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white70, fontSize: 13),
          ),
          if (_devCode != null) ...[
            const SizedBox(height: 12),
            Container(
              key: const Key('password-reset-dev-code'),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: .08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                l10n.tr(
                  fa: 'کد محیط توسعه: $_devCode',
                  en: 'Development code: $_devCode',
                ),
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70),
              ),
            ),
          ],
          const SizedBox(height: 20),
          _AuthInputTheme(
            child: Column(
              children: [
                FarmTextField(
                  key: const Key('password-reset-code'),
                  controller: _codeController,
                  label: l10n.tr(fa: 'کد بازیابی', en: 'Reset code'),
                  keyboardType: TextInputType.number,
                  textInputAction: TextInputAction.next,
                  prefixIcon: Icons.pin_outlined,
                  validator:
                      (value) =>
                          value == null || value.trim().length < 4
                              ? l10n.tr(
                                fa: 'کد بازیابی را وارد کنید',
                                en: 'Enter the reset code',
                              )
                              : null,
                ),
                const SizedBox(height: 12),
                FarmTextField(
                  key: const Key('password-reset-new-password'),
                  controller: _passwordController,
                  label: l10n.tr(fa: 'رمز جدید', en: 'New password'),
                  obscureText: !_passwordVisible,
                  textInputAction: TextInputAction.next,
                  prefixIcon: Icons.lock_outline_rounded,
                  suffixIcon: IconButton(
                    onPressed:
                        () => setState(
                          () => _passwordVisible = !_passwordVisible,
                        ),
                    icon: Icon(
                      _passwordVisible
                          ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined,
                    ),
                  ),
                  validator: (value) => _validatePassword(l10n, value),
                ),
                const SizedBox(height: 12),
                FarmTextField(
                  key: const Key('password-reset-confirm-password'),
                  controller: _confirmPasswordController,
                  label: l10n.tr(
                    fa: 'تکرار رمز جدید',
                    en: 'Confirm new password',
                  ),
                  obscureText: !_confirmPasswordVisible,
                  textInputAction: TextInputAction.done,
                  prefixIcon: Icons.lock_reset_rounded,
                  suffixIcon: IconButton(
                    onPressed:
                        () => setState(
                          () =>
                              _confirmPasswordVisible =
                                  !_confirmPasswordVisible,
                        ),
                    icon: Icon(
                      _confirmPasswordVisible
                          ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined,
                    ),
                  ),
                  validator:
                      (value) =>
                          value != _passwordController.text
                              ? l10n.tr(
                                fa: 'تکرار رمز با رمز جدید یکسان نیست',
                                en: 'Passwords do not match',
                              )
                              : null,
                ),
              ],
            ),
          ),
          if (_errorCode != null) _errorPanel(l10n),
          const SizedBox(height: 22),
          FarmButton(
            key: const Key('password-reset-confirm-action'),
            label: l10n.tr(fa: 'ثبت رمز جدید', en: 'Set new password'),
            icon: Icons.check_rounded,
            isLoading: _isLoading,
            onPressed: _isLoading ? null : _confirmReset,
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: _isLoading ? null : () => _requestCode(validate: false),
            child: Text(l10n.tr(fa: 'ارسال دوباره کد', en: 'Resend code')),
          ),
        ],
      ),
    );
  }

  Widget _successStep(AppLocalizations l10n) {
    return Column(
      key: const ValueKey('password-reset-success-step'),
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 16),
        const Icon(Icons.task_alt_rounded, color: Color(0xFFA6D99D), size: 64),
        const SizedBox(height: 18),
        Text(
          l10n.tr(fa: 'رمز عبور تغییر کرد', en: 'Password updated'),
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 22,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 10),
        Text(
          l10n.tr(
            fa: 'همه نشست‌های قبلی بسته شدند. اکنون با رمز جدید وارد شوید.',
            en: 'Previous sessions were closed. Sign in with your new password.',
          ),
          textAlign: TextAlign.center,
          style: const TextStyle(color: Colors.white70),
        ),
        const SizedBox(height: 28),
        FarmButton(
          key: const Key('password-reset-back-to-login'),
          label: l10n.tr(fa: 'بازگشت به ورود', en: 'Back to login'),
          icon: Icons.login_rounded,
          onPressed: _back,
        ),
      ],
    );
  }

  Widget _errorPanel(AppLocalizations l10n) {
    final message = switch (_errorCode) {
      'AUTH_PASSWORD_RESET_INVALID' => l10n.tr(
        fa: 'کد بازیابی صحیح نیست.',
        en: 'The reset code is invalid.',
      ),
      'AUTH_PASSWORD_RESET_EXPIRED' => l10n.tr(
        fa: 'زمان استفاده از کد تمام شده است. کد جدید بگیرید.',
        en: 'The reset code expired. Request a new one.',
      ),
      'AUTH_PASSWORD_RESET_TOO_MANY_ATTEMPTS' => l10n.tr(
        fa: 'تعداد تلاش‌ها زیاد شد. کد جدید بگیرید.',
        en: 'Too many attempts. Request a new code.',
      ),
      'VALIDATION_ERROR' => l10n.tr(
        fa: 'اطلاعات واردشده معتبر نیست.',
        en: 'The entered information is invalid.',
      ),
      'NETWORK_ERROR' => l10n.tr(
        fa: 'ارتباط با سرور برقرار نشد.',
        en: 'Could not connect to the server.',
      ),
      _ =>
        _errorMessage ??
            l10n.tr(
              fa: 'بازیابی رمز انجام نشد. دوباره تلاش کنید.',
              en: 'Password reset failed. Try again.',
            ),
    };
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.redAccent.withValues(alpha: .14),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Color(0xFFFFB4AB), fontSize: 12),
        ),
      ),
    );
  }

  String? _validateIdentifier(AppLocalizations l10n, String? value) {
    final identifier = value?.trim() ?? '';
    if (identifier.isEmpty) {
      return l10n.tr(
        fa: 'ایمیل یا شماره موبایل را وارد کنید',
        en: 'Enter your email or mobile number',
      );
    }
    final isEmail = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(identifier);
    final digits = identifier.replaceAll(RegExp(r'[^0-9۰-۹٠-٩]'), '');
    if (!isEmail && digits.length < 10) {
      return l10n.tr(
        fa: 'ایمیل یا شماره موبایل معتبر وارد کنید',
        en: 'Enter a valid email or mobile number',
      );
    }
    return null;
  }

  String? _validatePassword(AppLocalizations l10n, String? value) {
    final password = value ?? '';
    if (password.length < 8) {
      return l10n.tr(
        fa: 'رمز جدید باید حداقل ۸ کاراکتر باشد',
        en: 'Use at least 8 characters',
      );
    }
    return null;
  }
}

class _AuthInputTheme extends StatelessWidget {
  const _AuthInputTheme({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: Theme.of(context).copyWith(
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white.withValues(alpha: .06),
          labelStyle: const TextStyle(color: Colors.white70),
          prefixIconColor: Colors.white70,
          suffixIconColor: Colors.white70,
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
        iconTheme: const IconThemeData(color: Colors.white70),
      ),
      child: child,
    );
  }
}
