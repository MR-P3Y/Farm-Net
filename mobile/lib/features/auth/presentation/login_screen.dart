import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';
import 'otp_request_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController(text: 'admin@example.com');
  final _passwordController = TextEditingController(text: 'change-me');

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    await ref
        .read(authControllerProvider.notifier)
        .loginWithEmail(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
  }

  Future<void> _register() async {
    await ref
        .read(authControllerProvider.notifier)
        .registerWithEmail(
          email: _emailController.text.trim(),
          password: _passwordController.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          final isWide = r.width > 900; // برای تبلت‌های بزرگ و دسکتاپ
          final bgImage =
              r.isDesktop
                  ? 'assets/images/login_bg_web.webp'
                  : r.isTablet
                  ? 'assets/images/login_bg_tablet.webp'
                  : 'assets/images/login_bg_mobile.webp';

          return Stack(
            children: [
              // پس‌زمینه با تراز چپ برای وب تا تراکتور دیده شود
              Positioned.fill(
                child: Image.asset(
                  bgImage,
                  fit: BoxFit.cover,
                  alignment: isWide ? Alignment.centerLeft : Alignment.center,
                ),
              ),

              // لایه تیره کننده بسیار ملایم (کاهش یافته برای دیده شدن بک‌گراند)
              Positioned.fill(
                child: Container(color: Colors.black.withValues(alpha: 0.15)),
              ),

              // محتوای لاگین
              Align(
                alignment:
                    isWide ? Alignment.centerRight : const Alignment(0, -0.6),
                child: Padding(
                  padding:
                      isWide
                          ? EdgeInsets.only(right: r.width * 0.08)
                          : EdgeInsets.symmetric(horizontal: r.s(40)),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isWide ? 400 : 330),
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      child: FarmGlassCard(
                        borderRadius: 28,
                        opacity: 0.1, // افزایش شفافیت برای ایجاد حس ۵۰٪ شیشه‌ای
                        blur: 16,    // تاری بیشتر برای افکت شیشه‌ای قوی‌تر
                        padding: EdgeInsets.symmetric(
                          vertical: isWide ? 36 : 24,
                          horizontal: isWide ? 32 : 24,
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Icon(
                              Icons.eco_rounded,
                              color: Colors.white,
                              size: isWide ? 52 : 40,
                            ),
                            SizedBox(height: r.v(8)),
                            Text(
                              l10n.appName,
                              style: (isWide
                                      ? Theme.of(context).textTheme.headlineMedium
                                      : Theme.of(context).textTheme.headlineSmall)
                                  ?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 2,
                                shadows: [
                                  Shadow(
                                    color: Colors.black.withValues(alpha: 0.3),
                                    blurRadius: 10,
                                  ),
                                ],
                              ),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: isWide ? r.v(40) : r.v(24)),
                            Theme(
                              data: Theme.of(context).copyWith(
                                inputDecorationTheme: InputDecorationTheme(
                                  filled: true,
                                  fillColor: Colors.white.withValues(
                                    alpha: 0.05,
                                  ),
                                  labelStyle: const TextStyle(
                                    color: Colors.white70,
                                    fontSize: 13,
                                  ),
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 14,
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(14),
                                    borderSide: BorderSide(
                                      color: Colors.white.withValues(
                                        alpha: 0.15,
                                      ),
                                    ),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(14),
                                    borderSide: const BorderSide(
                                      color: Colors.white,
                                      width: 1,
                                    ),
                                  ),
                                ),
                              ),
                              child: Column(
                                children: [
                                  FarmTextField(
                                    controller: _emailController,
                                    label: l10n.emailOrUsername,
                                    keyboardType: TextInputType.emailAddress,
                                  ),
                                  SizedBox(height: r.v(16)),
                                  FarmTextField(
                                    controller: _passwordController,
                                    label: l10n.password,
                                    obscureText: true,
                                  ),
                                ],
                              ),
                            ),
                            if (auth.errorMessage != null) ...[
                              SizedBox(height: r.v(12)),
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.redAccent.withValues(
                                    alpha: 0.1,
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Text(
                                  auth.errorMessage!,
                                  style: const TextStyle(
                                    color: Colors.redAccent,
                                    fontSize: 11,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ],
                            SizedBox(height: isWide ? r.v(40) : r.v(28)),
                            FarmButton(
                              label: l10n.login,
                              isLoading: auth.isLoading,
                              onPressed: auth.isLoading ? null : _login,
                            ),
                            SizedBox(height: isWide ? r.v(24) : r.v(16)),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                _SecondaryButton(
                                  onPressed:
                                      auth.isLoading
                                          ? null
                                          : () {
                                            Navigator.of(context).push(
                                              MaterialPageRoute<void>(
                                                builder:
                                                    (_) =>
                                                        const OtpRequestScreen(),
                                              ),
                                            );
                                          },
                                  label: l10n.loginWithMobile,
                                ),
                                Container(
                                  height: 10,
                                  width: 1,
                                  margin: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                  ),
                                  color: Colors.white.withValues(alpha: 0.1),
                                ),
                                _SecondaryButton(
                                  onPressed: auth.isLoading ? null : _register,
                                  label: l10n.register,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
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
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}
