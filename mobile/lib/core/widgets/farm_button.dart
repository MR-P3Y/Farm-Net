import 'package:flutter/material.dart';

enum FarmButtonVariant { primary, secondary, outline, text, destructive }

class FarmButton extends StatelessWidget {
  const FarmButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.isLoading = false,
    this.variant = FarmButtonVariant.primary,
    this.icon,
    this.expand = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final FarmButtonVariant variant;
  final IconData? icon;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final callback = isLoading ? null : onPressed;
    final content = AnimatedSwitcher(
      duration: const Duration(milliseconds: 160),
      child:
          isLoading
              ? const SizedBox.square(
                key: ValueKey('loading'),
                dimension: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
              : Row(
                key: const ValueKey('label'),
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 19),
                    const SizedBox(width: 8),
                  ],
                  Flexible(child: Text(label, overflow: TextOverflow.ellipsis)),
                ],
              ),
    );
    final button = switch (variant) {
      FarmButtonVariant.primary => FilledButton(
        onPressed: callback,
        child: content,
      ),
      FarmButtonVariant.secondary => FilledButton.tonal(
        onPressed: callback,
        child: content,
      ),
      FarmButtonVariant.outline => OutlinedButton(
        onPressed: callback,
        child: content,
      ),
      FarmButtonVariant.text => TextButton(onPressed: callback, child: content),
      FarmButtonVariant.destructive => FilledButton(
        style: FilledButton.styleFrom(
          backgroundColor: Theme.of(context).colorScheme.error,
          foregroundColor: Theme.of(context).colorScheme.onError,
        ),
        onPressed: callback,
        child: content,
      ),
    };
    return expand ? SizedBox(width: double.infinity, child: button) : button;
  }
}
