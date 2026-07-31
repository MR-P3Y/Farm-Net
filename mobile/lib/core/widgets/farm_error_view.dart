import 'package:flutter/material.dart';

import '../localization/app_localizations.dart';
import '../theme/app_illustrations.dart';
import '../theme/app_spacing.dart';
import 'farm_button.dart';

class FarmErrorView extends StatelessWidget {
  const FarmErrorView({
    super.key,
    this.message,
    this.onRetry,
    this.isOffline = false,
  });

  final String? message;
  final VoidCallback? onRetry;
  final bool isOffline;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final label =
        message ?? (isOffline ? context.l10n.offline : context.l10n.error);
    return Center(
      child: Semantics(
        liveRegion: true,
        label: label,
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isOffline ? AppIllustrations.offline : AppIllustrations.error,
                size: 54,
                color: isOffline ? colors.onSurfaceVariant : colors.error,
              ),
              const SizedBox(height: AppSpacing.md),
              Text(label, textAlign: TextAlign.center),
              if (onRetry != null) ...[
                const SizedBox(height: AppSpacing.lg),
                FarmButton(
                  label: context.l10n.retry,
                  onPressed: onRetry,
                  icon: Icons.refresh_rounded,
                  variant: FarmButtonVariant.outline,
                  expand: false,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
