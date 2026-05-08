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
      appBar: AppBar(
        title: const Text('تأیید کد'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Padding(
                padding: r.pagePadding(),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('کد ارسال‌شده برای ${widget.phone} را وارد کنید'),
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
          );
        },
      ),
    );
  }
}
