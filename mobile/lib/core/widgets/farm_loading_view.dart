import 'package:flutter/material.dart';

import '../localization/app_localizations.dart';
import '../theme/app_spacing.dart';

class FarmLoadingView extends StatelessWidget {
  const FarmLoadingView({super.key, this.message, this.compact = false});

  final String? message;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final label = message ?? context.l10n.loading;
    return Center(
      child: Semantics(
        liveRegion: true,
        label: label,
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox.square(
                dimension: 28,
                child: CircularProgressIndicator(strokeWidth: 3),
              ),
              if (!compact) ...[
                const SizedBox(height: AppSpacing.md),
                Text(label),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
