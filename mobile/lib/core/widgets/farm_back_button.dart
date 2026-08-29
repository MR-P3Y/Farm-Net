import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../localization/app_localizations.dart';
import '../theme/app_icons.dart';
import 'farm_circular_glass_button.dart';

class FarmBackButton extends StatelessWidget {
  const FarmBackButton({
    super.key,
    this.color,
    this.fallbackLocation,
    this.onPressed,
  });

  final Color? color;
  final String? fallbackLocation;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return FarmCircularGlassButton(
      icon: AppIcons.back,
      size: 18,
      padding: 8,
      color: color,
      tooltip: context.l10n.back,
      onTap:
          onPressed ??
          () {
            if (Navigator.canPop(context)) {
              Navigator.maybePop(context);
              return;
            }
            final fallback = fallbackLocation;
            if (fallback != null && fallback.isNotEmpty) {
              context.go(fallback);
            }
          },
    );
  }
}
