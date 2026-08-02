import 'package:flutter/material.dart';

import '../../../../core/localization/app_localizations.dart';
import '../../data/farm_models.dart';

class FarmArchiveRequest {
  const FarmArchiveRequest({this.reason});

  final String? reason;
}

Future<FarmArchiveRequest?> showFarmArchiveDialog(
  BuildContext context,
  FarmModel farm,
) async {
  final reason = TextEditingController();
  final result = await showDialog<FarmArchiveRequest>(
    context: context,
    builder: (dialogContext) {
      final l10n = dialogContext.l10n;
      return AlertDialog(
        icon: const Icon(Icons.delete_outline_rounded),
        title: Text(l10n.tr(fa: 'حذف مزرعه؟', en: 'Remove farm?')),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                l10n.tr(
                  fa:
                      '«${farm.name}» از فهرست فعال حذف و بایگانی می‌شود. قطعات، عملیات و سوابق آن پاک نمی‌شوند و بعداً قابل بازیابی است.',
                  en:
                      '“${farm.name}” will be removed from the active list and archived. Its Plots, operations, and history are preserved and can be restored.',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: reason,
                maxLength: 500,
                minLines: 2,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: l10n.tr(
                    fa: 'دلیل حذف (اختیاری)',
                    en: 'Reason (optional)',
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: Text(l10n.tr(fa: 'انصراف', en: 'Cancel')),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(dialogContext).colorScheme.error,
              foregroundColor: Theme.of(dialogContext).colorScheme.onError,
            ),
            onPressed: () {
              final value = reason.text.trim();
              Navigator.pop(
                dialogContext,
                FarmArchiveRequest(reason: value.isEmpty ? null : value),
              );
            },
            child: Text(l10n.tr(fa: 'حذف از فهرست', en: 'Remove')),
          ),
        ],
      );
    },
  );
  reason.dispose();
  return result;
}

Future<bool> showFarmRestoreDialog(BuildContext context, FarmModel farm) async {
  return await showDialog<bool>(
        context: context,
        builder: (dialogContext) {
          final l10n = dialogContext.l10n;
          return AlertDialog(
            icon: const Icon(Icons.restore_rounded),
            title: Text(l10n.tr(fa: 'بازیابی مزرعه؟', en: 'Restore farm?')),
            content: Text(
              l10n.tr(
                fa: '«${farm.name}» دوباره به فهرست مزارع فعال برمی‌گردد.',
                en: '“${farm.name}” will return to the active Farms list.',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: Text(l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton.icon(
                onPressed: () => Navigator.pop(dialogContext, true),
                icon: const Icon(Icons.restore_rounded),
                label: Text(l10n.tr(fa: 'بازیابی', en: 'Restore')),
              ),
            ],
          );
        },
      ) ??
      false;
}
