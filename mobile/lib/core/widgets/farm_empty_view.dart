import 'package:flutter/material.dart';

import '../localization/app_localizations.dart';
import '../theme/app_illustrations.dart';
import '../theme/app_spacing.dart';
import 'farm_button.dart';

class FarmEmptyView extends StatelessWidget {
  const FarmEmptyView({
    super.key,
    this.message,
    this.title,
    this.icon = AppIllustrations.empty,
    this.actionLabel,
    this.onAction,
  });

  final String? message;
  final String? title;
  final IconData icon;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 52, color: colors.primary.withValues(alpha: 0.72)),
            const SizedBox(height: AppSpacing.md),
            if (title != null) ...[
              Text(title!, style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: AppSpacing.xs),
            ],
            Text(
              message ?? context.l10n.empty,
              textAlign: TextAlign.center,
              style: TextStyle(color: colors.onSurfaceVariant),
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: AppSpacing.lg),
              FarmButton(
                label: actionLabel!,
                onPressed: onAction,
                variant: FarmButtonVariant.outline,
                expand: false,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
