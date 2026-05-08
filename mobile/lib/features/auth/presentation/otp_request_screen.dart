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
      appBar: AppBar(
        title: const Text('ورود با موبایل'),
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
          );
        },
      ),
    );
  }
}
