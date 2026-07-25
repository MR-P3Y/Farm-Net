import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../state/auth_controller.dart';

class OtpVerifyScreen extends ConsumerStatefulWidget {
  const OtpVerifyScreen({super.key, required this.phone});

  final String phone;

  @override
  ConsumerState<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends ConsumerState<OtpVerifyScreen> {
  final _codeController = TextEditingController(text: '111111');

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _verifyOtp() async {
    final ok = await ref
        .read(authControllerProvider.notifier)
        .verifyOtp(phone: widget.phone, code: _codeController.text.trim());

    if (!ok || !mounted) return;

    Navigator.of(context).popUntil((route) => route.isFirst);
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
                              'تأیید کد',
                              style: Theme.of(context).textTheme.headlineSmall,
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: r.v(16)),
                            Text(
                              'کد ارسال‌شده برای ${widget.phone} را وارد کنید',
                            ),
                            if (auth.devOtpCode != null) ...[
                              SizedBox(height: r.v(8)),
                              Text(
                                'کد توسعه: ${auth.devOtpCode}',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                            SizedBox(height: r.v(16)),
                            FarmTextField(
                              controller: _codeController,
                              label: 'کد تأیید',
                              keyboardType: TextInputType.number,
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
                              label: 'تأیید و ورود',
                              isLoading: auth.isLoading,
                              onPressed: auth.isLoading ? null : _verifyOtp,
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
