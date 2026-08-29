import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';
import '../state/auth_state.dart';
import 'auth_page_shell.dart';
import 'otp_request_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _passwordVisible = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    FocusManager.instance.primaryFocus?.unfocus();
    await ref
        .read(authControllerProvider.notifier)
        .loginWithEmail(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    final l10n = context.l10n;

    return AuthPageShell(
      maxWidth: 400,
      mobileAlignment: const Alignment(0, -0.78),
      desktopAlignment: const AlignmentDirectional(1, -0.42),
      child: FarmGlassCard(
        key: const Key('email-login-card'),
        borderRadius: 28,
        opacity: .1,
        blur: 16,
        padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.eco_rounded, color: Colors.white, size: 44),
            const SizedBox(height: 8),
            Text(
              l10n.appName,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
                shadows: [
                  Shadow(
                    color: Colors.black.withValues(alpha: .3),
                    blurRadius: 10,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 26),
            Theme(
              data: _inputTheme(context),
              child: Form(
                key: _formKey,
                child: AutofillGroup(
                  child: Column(
                    children: [
                      FarmTextField(
                        key: const Key('login-email'),
                        controller: _emailController,
                        label: l10n.emailOrUsername,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        prefixIcon: Icons.alternate_email_rounded,
                        autofillHints: const [
                          AutofillHints.email,
                          AutofillHints.username,
                        ],
                        autocorrect: false,
                        enableSuggestions: false,
                        validator: (value) => _validateEmail(context, value),
                      ),
                      const SizedBox(height: 14),
                      FarmTextField(
                        key: const Key('login-password'),
                        controller: _passwordController,
                        label: l10n.password,
                        obscureText: !_passwordVisible,
                        textInputAction: TextInputAction.done,
                        prefixIcon: Icons.lock_outline_rounded,
                        autofillHints: const [AutofillHints.password],
                        autocorrect: false,
                        enableSuggestions: false,
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
                        validator:
                            (value) =>
                                value == null || value.isEmpty
                                    ? l10n.tr(
                                      fa: 'رمز عبور را وارد کنید',
                                      en: 'Enter your password',
                                    )
                                    : null,
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: TextButton(
                key: const Key('forgot-password-link'),
                onPressed:
                    auth.isLoading
                        ? null
                        : () {
                          ref
                              .read(authControllerProvider.notifier)
                              .clearError();
                          context.push('/forgot-password');
                        },
                child: Text(
                  l10n.tr(
                    fa: 'رمز عبور را فراموش کرده‌اید؟',
                    en: 'Forgot password?',
                  ),
                  style: const TextStyle(color: Colors.white70),
                ),
              ),
            ),
            if (auth.errorMessage != null) ...[
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.redAccent.withValues(alpha: .14),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _loginErrorMessage(context, auth),
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    color: Color(0xFFFFB4AB),
                    fontSize: 12,
                  ),
                ),
              ),
            ],
            const SizedBox(height: 20),
            FarmButton(
              key: const Key('email-login-action'),
              label: l10n.login,
              icon: Icons.login_rounded,
              isLoading: auth.isLoading,
              onPressed: auth.isLoading ? null : _login,
            ),
            const SizedBox(height: 16),
            Wrap(
              alignment: WrapAlignment.center,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 8,
              runSpacing: 6,
              children: [
                _SecondaryButton(
                  onPressed:
                      auth.isLoading
                          ? null
                          : () {
                            ref
                                .read(authControllerProvider.notifier)
                                .clearError();
                            Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) => const OtpRequestScreen(),
                              ),
                            );
                          },
                  label: l10n.loginWithMobile,
                ),
                Container(
                  height: 14,
                  width: 1,
                  color: Colors.white.withValues(alpha: .2),
                ),
                _SecondaryButton(
                  onPressed:
                      auth.isLoading
                          ? null
                          : () {
                            ref
                                .read(authControllerProvider.notifier)
                                .clearError();
                            context.push('/register');
                          },
                  label: l10n.register,
                ),
              ],
            ),
          ],
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
    );
  }

  String? _validateEmail(BuildContext context, String? value) {
    final email = value?.trim() ?? '';
    if (email.isEmpty) {
      return context.l10n.tr(fa: 'ایمیل را وارد کنید', en: 'Enter your email');
    }
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(email)) {
      return context.l10n.tr(
        fa: 'ایمیل معتبر وارد کنید',
        en: 'Enter a valid email',
      );
    }
    return null;
  }

  String _loginErrorMessage(BuildContext context, AuthState state) {
    final l10n = context.l10n;
    return switch (state.errorCode) {
      'AUTH_INVALID_CREDENTIALS' => l10n.tr(
        fa: 'ایمیل یا رمز عبور درست نیست.',
        en: 'The email or password is incorrect.',
      ),
      'VALIDATION_ERROR' => l10n.tr(
        fa: 'اطلاعات ورود را کامل و صحیح وارد کنید.',
        en: 'Enter valid login information.',
      ),
      'NETWORK_ERROR' => l10n.tr(
        fa: 'ارتباط با سرور برقرار نشد. اتصال را بررسی کنید.',
        en: 'Could not connect to the server. Check your connection.',
      ),
      _ => l10n.tr(
        fa: 'ورود انجام نشد. دوباره تلاش کنید.',
        en: state.errorMessage ?? 'Login failed. Try again.',
      ),
    };
  }
}

class _SecondaryButton extends StatelessWidget {
  const _SecondaryButton({required this.onPressed, required this.label});

  final VoidCallback? onPressed;
  final String label;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onPressed,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
