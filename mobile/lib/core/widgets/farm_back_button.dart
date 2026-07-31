import 'package:flutter/material.dart';
import '../localization/app_localizations.dart';
import '../theme/app_icons.dart';
import 'farm_circular_glass_button.dart';

class FarmBackButton extends StatelessWidget {
  const FarmBackButton({super.key, this.color});

  final Color? color;

  @override
  Widget build(BuildContext context) {
    return FarmCircularGlassButton(
      icon: AppIcons.back,
      size: 18,
      padding: 8,
      tooltip: context.l10n.back,
      onTap: () => Navigator.maybePop(context),
    );
  }
}
