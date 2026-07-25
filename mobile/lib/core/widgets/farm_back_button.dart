import 'package:flutter/material.dart';
import 'farm_circular_glass_button.dart';

class FarmBackButton extends StatelessWidget {
  const FarmBackButton({super.key, this.color});

  final Color? color;

  @override
  Widget build(BuildContext context) {
    // در محیط RTL (فارسی)، فلش برگشت باید به سمت راست باشد
    return FarmCircularGlassButton(
      icon: Icons.arrow_forward_ios_rounded,
      size: 18,
      padding: 8,
      onTap: () => Navigator.maybePop(context),
    );
  }
}
