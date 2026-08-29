import 'package:flutter/material.dart';
import 'farm_glass_card.dart';

class FarmCircularGlassButton extends StatelessWidget {
  const FarmCircularGlassButton({
    super.key,
    required this.icon,
    required this.onTap,
    this.size = 24,
    this.padding = 10,
    this.tooltip,
    this.color,
  });

  final IconData icon;
  final VoidCallback? onTap;
  final double size;
  final double padding;
  final String? tooltip;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final button = Opacity(
      opacity: onTap == null ? 0.45 : 1,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(50),
        child: FarmGlassCard(
          borderRadius: 50,
          blur: 10,
          opacity: 0.1,
          padding: EdgeInsets.all(padding),
          child: Icon(icon, size: size, color: color),
        ),
      ),
    );
    return tooltip == null ? button : Tooltip(message: tooltip!, child: button);
  }
}
