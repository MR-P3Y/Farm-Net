import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';
import 'otp_verify_screen.dart';

class OtpRequestScreen extends ConsumerStatefulWidget {
  const OtpRequestScreen({super.key});

  @override
  ConsumerState<OtpRequestScreen> createState() => _OtpRequestScreenState();
}

class _OtpRequestScreenState extends ConsumerState<OtpRequestScreen> {
  final _phoneController = TextEditingController(text: '09123456789');

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    final ok = await ref
        .read(authControllerProvider.notifier)
        .requestOtp(phone: _phoneController.text.trim());

    if (!ok || !mounted) return;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (_) => OtpVerifyScreen(phone: _phoneController.text.trim()),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);

    return Scaffold(
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          final bgImage =
              r.isDesktop
                  ? 'assets/images/login_bg_web.webp'
                  : r.isTablet
                  ? 'assets/images/login_bg_tablet.webp'
                  : 'assets/images/login_bg_mobile.webp';

          return Stack(
            children: [
              Positioned.fill(child: Image.asset(bgImage, fit: BoxFit.cover)),
              AppBar(
                backgroundColor: Colors.transparent,
                elevation: 0,
                leading: IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: SingleChildScrollView(
                    padding: r.pagePadding(),
                    child: Card(
                      color: Theme.of(
                        context,
                      ).colorScheme.surface.withAlpha(220),
                      elevation: 8,
                      child: Padding(
                        padding: EdgeInsets.all(r.s(20)),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              'ورود با موبایل',
                              style: Theme.of(context).textTheme.headlineSmall,
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: r.v(24)),
                            FarmTextField(
                              controller: _phoneController,
                              label: 'شماره موبایل',
                              keyboardType: TextInputType.phone,
                            ),
                            if (auth.errorMessage != null) ...[
                              SizedBox(height: r.v(12)),
                              Text(
                                auth.errorMessage!,
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              ),
                            ],
                            SizedBox(height: r.v(20)),
                            FarmButton(
                              label: 'دریافت کد',
                              isLoading: auth.isLoading,
                              onPressed: auth.isLoading ? null : _requestOtp,
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
