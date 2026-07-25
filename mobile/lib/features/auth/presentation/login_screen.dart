import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
                    isWide ? AlignmentDirectional.centerEnd : Alignment.center,
                child: Padding(
                  padding:
                      isWide
                          ? EdgeInsetsDirectional.only(end: r.width * 0.08)
                          : EdgeInsets.symmetric(horizontal: r.s(20)),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 400),
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      child: FarmGlassCard(
                        borderRadius: 32,
                        opacity: 0.05, // بسیار شفاف برای دیده شدن بک‌گراند
                        blur: 8, // تاری ملایم‌تر (Lighter Blur)
                        padding: const EdgeInsets.symmetric(
                          vertical: 32,
                          horizontal: 28,
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min, // جلوگیری از Overflow
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            const Icon(
                              Icons.eco_rounded,
                              color: Colors.white,
                              size: 48,
                            ),
                            SizedBox(height: r.v(8)),
                            Text(
                              'فارم نت',
                              style: Theme.of(
                                context,
                              ).textTheme.headlineMedium?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 1.5,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: r.v(32)),
                            Theme(
                              data: Theme.of(context).copyWith(
                                inputDecorationTheme: InputDecorationTheme(
                                  filled: true,
                                  fillColor: Colors.white.withValues(
                                    alpha: 0.05,
                                  ),
                                  labelStyle: const TextStyle(
                                    color: Colors.white60,
                                    fontSize: 13,
                                  ),
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 16,
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(16),
                                    borderSide: BorderSide(
                                      color: Colors.white.withValues(
                                        alpha: 0.15,
                                      ),
                                    ),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(16),
                                    borderSide: const BorderSide(
                                      color: Colors.white54,
                                    ),
                                  ),
                                ),
                              ),
                              child: Column(
                                children: [
                                  FarmTextField(
                                    controller: _emailController,
                                    label: 'ایمیل یا نام کاربری',
                                    keyboardType: TextInputType.emailAddress,
                                  ),
                                  SizedBox(height: r.v(16)),
                                  FarmTextField(
                                    controller: _passwordController,
                                    label: 'رمز عبور',
                                    obscureText: true,
                                  ),
                                ],
                              ),
                            ),
                            if (auth.errorMessage != null) ...[
                              SizedBox(height: r.v(12)),
                              Text(
                                auth.errorMessage!,
                                style: const TextStyle(
                                  color: Colors.redAccent,
                                  fontSize: 12,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                            SizedBox(height: r.v(32)),
                            FarmButton(
                              label: 'ورود به سیستم',
                              isLoading: auth.isLoading,
                              onPressed: auth.isLoading ? null : _login,
                            ),
                            SizedBox(height: r.v(24)),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                TextButton(
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
                                  style: TextButton.styleFrom(
                                    foregroundColor: Colors.white70,
                                    textStyle: const TextStyle(fontSize: 13),
                                  ),
                                  child: const Text('ورود با موبایل'),
                                ),
                                Text(
                                  '|',
                                  style: TextStyle(
                                    color: Colors.white.withValues(alpha: 0.2),
                                  ),
                                ),
                                TextButton(
                                  onPressed: auth.isLoading ? null : _register,
                                  style: TextButton.styleFrom(
                                    foregroundColor: Colors.white70,
                                    textStyle: const TextStyle(fontSize: 13),
                                  ),
                                  child: const Text('ثبت‌نام'),
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
