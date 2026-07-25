import 'package:flutter/material.dart';
import 'farm_glass_card.dart';

class FarmSearchField extends StatelessWidget {
  const FarmSearchField({
    super.key,
    required this.controller,
    required this.onChanged,
    this.hint = 'جستجو...',
  });

  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final String hint;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return FarmGlassCard(
      borderRadius: 20,
      blur: 10,
      opacity: isDark ? 0.1 : 0.6,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        style: TextStyle(
          color: isDark ? Colors.white : const Color(0xFF1B5E20),
          fontWeight: FontWeight.w600,
        ),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(
            color: isDark ? Colors.white54 : Colors.black38,
            fontWeight: FontWeight.normal,
          ),
          border: InputBorder.none,
          icon: Icon(
            Icons.search_rounded,
            color: isDark ? Colors.white70 : const Color(0xFF2E7D32),
          ),
          suffixIcon: controller.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.close_rounded, size: 20),
                  onPressed: () {
                    controller.clear();
                    onChanged('');
                  },
                )
              : null,
        ),
      ),
    );
  }
}
