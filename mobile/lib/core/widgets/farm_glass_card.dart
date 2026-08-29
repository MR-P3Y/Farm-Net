import 'dart:ui';
import 'package:flutter/material.dart';

import '../theme/app_radius.dart';
import '../theme/app_theme_extensions.dart';

class FarmGlassCard extends StatelessWidget {
  const FarmGlassCard({
    super.key,
    required this.child,
    this.blur,
    this.opacity,
    this.borderRadius = AppRadius.lg,
    this.padding,
    this.enableBlur = true,
  });

  final Widget child;
  final double? blur;
  final double? opacity;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;
  final bool enableBlur;

  @override
  Widget build(BuildContext context) {
    final glass = context.glassTheme;
    final surface =
        enableBlur
            ? opacity == null
                ? glass.surface
                : glass.surface.withValues(alpha: opacity!)
            : glass.surfaceStrong.withValues(
              alpha: opacity == null ? 0.9 : 0.68 + (opacity! * 0.24),
            );
    final content = Container(
      padding: padding ?? const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: surface,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(color: glass.border, width: 1),
        boxShadow: [
          BoxShadow(color: glass.shadow, blurRadius: 20, spreadRadius: -5),
        ],
      ),
      child: child,
    );

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child:
          enableBlur
              ? BackdropFilter(
                filter: ImageFilter.blur(
                  sigmaX: blur ?? glass.blur,
                  sigmaY: blur ?? glass.blur,
                ),
                child: content,
              )
              : content,
    );
  }
}
