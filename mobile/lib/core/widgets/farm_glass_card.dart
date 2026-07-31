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
  });

  final Widget child;
  final double? blur;
  final double? opacity;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final glass = context.glassTheme;
    final surface =
        opacity == null
            ? glass.surface
            : glass.surface.withValues(alpha: opacity!);
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blur ?? glass.blur,
          sigmaY: blur ?? glass.blur,
        ),
        child: Container(
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
        ),
      ),
    );
  }
}
