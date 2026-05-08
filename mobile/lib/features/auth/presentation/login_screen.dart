import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
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
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: SingleChildScrollView(
                padding: r.pagePadding(),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(r.s(20)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'ورود به فارم نت',
                          style: Theme.of(context).textTheme.headlineSmall,
                          textAlign: TextAlign.center,
                        ),
                        SizedBox(height: r.v(24)),
                        FarmTextField(
                          controller: _emailController,
                          label: 'ایمیل',
                          keyboardType: TextInputType.emailAddress,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _passwordController,
                          label: 'رمز عبور',
                          obscureText: true,
                        ),
                        if (auth.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            auth.errorMessage!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        FarmButton(
                          label: 'ورود با ایمیل',
                          isLoading: auth.isLoading,
                          onPressed: auth.isLoading ? null : _login,
                        ),
                        SizedBox(height: r.v(8)),
                        OutlinedButton(
                          onPressed: auth.isLoading ? null : _register,
                          child: const Text('ثبت‌نام با ایمیل'),
                        ),
                        SizedBox(height: r.v(12)),
                        TextButton(
                          onPressed:
                              auth.isLoading
                                  ? null
                                  : () {
                                    Navigator.of(context).push(
                                      MaterialPageRoute<void>(
                                        builder:
                                            (_) => const OtpRequestScreen(),
                                      ),
                                    );
                                  },
                          child: const Text('ورود با شماره موبایل'),
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
