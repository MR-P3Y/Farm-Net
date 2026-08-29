import 'package:flutter/material.dart';

/// Shared bottom action used for the primary commitment on detail screens.
class FarmPrimaryActionBar extends StatelessWidget {
  const FarmPrimaryActionBar({
    required this.label,
    required this.icon,
    required this.onPressed,
    this.isLoading = false,
    this.loadingLabel,
    super.key,
  });

  final String label;
  final IconData icon;
  final VoidCallback? onPressed;
  final bool isLoading;
  final String? loadingLabel;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final effectiveLabel = isLoading ? loadingLabel ?? label : label;
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
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: isLoading ? null : onPressed,
                  style:
                      isLoading
                          ? FilledButton.styleFrom(
                            disabledBackgroundColor: colors.primary,
                            disabledForegroundColor: colors.onPrimary,
                          )
                          : null,
                  icon: AnimatedSwitcher(
                    duration: const Duration(milliseconds: 180),
                    child:
                        isLoading
                            ? SizedBox.square(
                              key: const Key('farm-primary-action-progress'),
                              dimension: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.4,
                                color: colors.onPrimary,
                              ),
                            )
                            : Icon(
                              icon,
                              key: const Key('farm-primary-action-icon'),
                            ),
                  ),
                  label: AnimatedSwitcher(
                    duration: const Duration(milliseconds: 180),
                    child: Text(effectiveLabel, key: ValueKey(effectiveLabel)),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
