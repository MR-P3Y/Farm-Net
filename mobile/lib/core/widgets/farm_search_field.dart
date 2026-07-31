import 'package:flutter/material.dart';

import '../localization/app_localizations.dart';
import '../theme/app_icons.dart';
import 'farm_glass_card.dart';

class FarmSearchField extends StatelessWidget {
  const FarmSearchField({
    super.key,
    required this.controller,
    required this.onChanged,
    this.hint,
    this.onSubmitted,
    this.autofocus = false,
  });

  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final String? hint;
  final ValueChanged<String>? onSubmitted;
  final bool autofocus;

  @override
  Widget build(BuildContext context) {
    return FarmGlassCard(
      borderRadius: 20,
      blur: 10,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        onSubmitted: onSubmitted,
        autofocus: autofocus,
        textInputAction: TextInputAction.search,
        decoration: InputDecoration(
          hintText: hint ?? context.l10n.search,
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: InputBorder.none,
          filled: false,
          icon: const Icon(AppIcons.search),
          suffixIcon:
              controller.text.isNotEmpty
                  ? IconButton(
                    tooltip: context.l10n.close,
                    icon: const Icon(AppIcons.close, size: 20),
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
