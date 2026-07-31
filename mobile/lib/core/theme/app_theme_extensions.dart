import 'package:flutter/material.dart';

@immutable
class FarmGlassTheme extends ThemeExtension<FarmGlassTheme> {
  const FarmGlassTheme({
    required this.surface,
    required this.surfaceStrong,
    required this.border,
    required this.highlight,
    required this.shadow,
    required this.blur,
  });

  final Color surface;
  final Color surfaceStrong;
  final Color border;
  final Color highlight;
  final Color shadow;
  final double blur;

  @override
  FarmGlassTheme copyWith({
    Color? surface,
    Color? surfaceStrong,
    Color? border,
    Color? highlight,
    Color? shadow,
    double? blur,
  }) {
    return FarmGlassTheme(
      surface: surface ?? this.surface,
      surfaceStrong: surfaceStrong ?? this.surfaceStrong,
      border: border ?? this.border,
      highlight: highlight ?? this.highlight,
      shadow: shadow ?? this.shadow,
      blur: blur ?? this.blur,
    );
  }

  @override
  FarmGlassTheme lerp(covariant FarmGlassTheme? other, double t) {
    if (other == null) return this;
    return FarmGlassTheme(
      surface: Color.lerp(surface, other.surface, t)!,
      surfaceStrong: Color.lerp(surfaceStrong, other.surfaceStrong, t)!,
      border: Color.lerp(border, other.border, t)!,
      highlight: Color.lerp(highlight, other.highlight, t)!,
      shadow: Color.lerp(shadow, other.shadow, t)!,
      blur: blur + (other.blur - blur) * t,
    );
  }
}

extension FarmThemeX on BuildContext {
  FarmGlassTheme get glassTheme => Theme.of(this).extension<FarmGlassTheme>()!;
}
