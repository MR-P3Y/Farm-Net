import 'package:flutter/material.dart';

import '../../../core/widgets/farm_button.dart';

class ServiceAction {
  const ServiceAction({
    required this.label,
    required this.icon,
    required this.onPressed,
    this.variant = FarmButtonVariant.primary,
    this.isLoading = false,
  });

  final String label;
  final IconData icon;
  final VoidCallback? onPressed;
  final FarmButtonVariant variant;
  final bool isLoading;
}

/// Compact, safe-area-aware actions that stay visible while details scroll.
class ServiceFloatingActionBar extends StatelessWidget {
  const ServiceFloatingActionBar({
    this.primary,
    this.secondary,
    this.tertiary,
    super.key,
  }) : assert(primary != null || secondary != null || tertiary != null);

  final ServiceAction? primary;
  final ServiceAction? secondary;
  final ServiceAction? tertiary;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return SafeArea(
      minimum: const EdgeInsets.fromLTRB(12, 6, 12, 10),
      child: Center(
        heightFactor: 1,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 760),
          child: Material(
            elevation: 8,
            shadowColor: colors.shadow.withValues(alpha: .18),
            color: colors.surfaceContainerHigh,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(22),
              side: BorderSide(
                color: colors.outlineVariant.withValues(alpha: .65),
              ),
            ),
            clipBehavior: Clip.antiAlias,
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (primary != null || secondary != null)
                    Row(
                      children: [
                        if (secondary != null) ...[
                          Expanded(child: _ActionButton(action: secondary!)),
                          if (primary != null) const SizedBox(width: 8),
                        ],
                        if (primary != null)
                          Expanded(child: _ActionButton(action: primary!)),
                      ],
                    ),
                  if (tertiary != null) ...[
                    if (primary != null || secondary != null)
                      const SizedBox(height: 4),
                    SizedBox(
                      width: double.infinity,
                      child: _ActionButton(action: tertiary!),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({required this.action});

  final ServiceAction action;

  @override
  Widget build(BuildContext context) => FarmButton(
    label: action.label,
    icon: action.icon,
    variant: action.variant,
    isLoading: action.isLoading,
    expand: true,
    onPressed: action.onPressed,
  );
}
