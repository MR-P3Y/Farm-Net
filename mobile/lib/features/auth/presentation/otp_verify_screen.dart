import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
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
    final l10n = context.l10n;

    return Scaffold(
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          final isWide = r.width > 900;
          final bgImage =
              r.isDesktop
                  ? 'assets/images/login_bg_web.webp'
                  : r.isTablet
                  ? 'assets/images/login_bg_tablet.webp'
                  : 'assets/images/login_bg_mobile.webp';

          return Stack(
            children: [
              // پس‌زمینه
              Positioned.fill(
                child: Image.asset(
                  bgImage,
                  fit: BoxFit.cover,
                  alignment: isWide ? Alignment.centerLeft : Alignment.center,
                ),
              ),
              // لایه تیره کننده ملایم
              Positioned.fill(
                child: Container(color: Colors.black.withValues(alpha: 0.15)),
              ),
              // محتوا
              Align(
                alignment:
                    isWide
                        ? AlignmentDirectional.centerStart
                        : const Alignment(0, -0.6),
                child: Padding(
                  padding:
                      isWide
                          ? EdgeInsetsDirectional.only(start: r.width * 0.08)
                          : EdgeInsets.symmetric(horizontal: r.s(40)),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: isWide ? 400 : 330),
                    child: SingleChildScrollView(
                      child: FarmGlassCard(
                        borderRadius: 28,
                        opacity: 0.1,
                        blur: 16,
                        padding: const EdgeInsetsDirectional.fromSTEB(
                          24,
                          12,
                          24,
                          32,
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // دکمه برگشت داخل باکس
                            Align(
                              alignment: AlignmentDirectional.centerStart,
                              child: IconButton(
                                icon: const Icon(
                                  Icons.arrow_forward_ios_rounded,
                                  color: Colors.white70,
                                  size: 20,
                                ),
                                onPressed: () => Navigator.pop(context),
                              ),
                            ),
                            const Icon(
                              Icons.mark_email_read_rounded,
                              color: Colors.white,
                              size: 48,
                            ),
                            const SizedBox(height: 16),
                            Text(
                              l10n.verifyCode,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 12),
                            Text(
                              l10n.tr(
                                fa:
                                    'کد ارسال‌شده برای ${widget.phone} را وارد کنید',
                                en: 'Enter the code sent to ${widget.phone}',
                              ),
                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 13,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            if (auth.errorMessage != null) ...[
                              const SizedBox(height: 8),
                              Text(
                                l10n.tr(
                                  fa: 'کد توسعه: ${auth.devOtpCode}',
                                  en: 'Development code: ${auth.devOtpCode}',
                                ),
                                style: const TextStyle(
                                  color: Colors.white54,
                                  fontSize: 11,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                            const SizedBox(height: 32),
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
                                    ),
                                  ),
                                ),
                              ),
                              child: FarmTextField(
                                controller: _codeController,
                                label: l10n.verificationCode,
                                keyboardType: TextInputType.number,
                              ),
                            ),
                            if (auth.errorMessage != null) ...[
                              const SizedBox(height: 12),
                              Text(
                                auth.errorMessage!,
                                style: const TextStyle(
                                  color: Colors.redAccent,
                                  fontSize: 11,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                            const SizedBox(height: 32),
                            FarmButton(
                              label: l10n.verifyAndLogin,
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
