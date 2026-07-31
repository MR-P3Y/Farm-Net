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
  });

  final IconData icon;
  final VoidCallback onTap;
  final double size;
  final double padding;
  final String? tooltip;

  @override
  Widget build(BuildContext context) {
    final button = InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(50),
      child: FarmGlassCard(
        borderRadius: 50,
        blur: 10,
        opacity: 0.1,
        padding: EdgeInsets.all(padding),
        child: Icon(icon, size: size),
      ),
    );
    return tooltip == null ? button : Tooltip(message: tooltip!, child: button);
  }
}
