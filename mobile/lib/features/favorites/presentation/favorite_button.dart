import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../data/favorite_models.dart';
import '../state/favorites_controller.dart';

class FavoriteIconButton extends ConsumerStatefulWidget {
  const FavoriteIconButton({
    required this.subjectType,
    required this.subjectId,
    this.onResult,
    super.key,
  });

  final FavoriteSubjectType subjectType;
  final int subjectId;
  final ValueChanged<bool>? onResult;

  @override
  ConsumerState<FavoriteIconButton> createState() => _FavoriteIconButtonState();
}

class _FavoriteIconButtonState extends ConsumerState<FavoriteIconButton> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(favoritesControllerProvider.notifier).loadStatus(
        widget.subjectType,
        [widget.subjectId],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final itemKey = FavoritesController.key(
      widget.subjectType,
      widget.subjectId,
    );
    final state = ref.watch(favoritesControllerProvider);
    final isFavorite = state.favoriteKeys.contains(itemKey);
    final isLoading = state.loadingKeys.contains(itemKey);
    final label = context.l10n.tr(
      fa: isFavorite ? 'حذف از علاقه‌مندی‌ها' : 'افزودن به علاقه‌مندی‌ها',
      en: isFavorite ? 'Remove from favorites' : 'Add to favorites',
    );

    return IconButton(
      tooltip: label,
      onPressed:
          isLoading
              ? null
              : () async {
                final result = await ref
                    .read(favoritesControllerProvider.notifier)
                    .toggle(widget.subjectType, widget.subjectId);
                if (!context.mounted) return;
                widget.onResult?.call(result);
                final error =
                    ref.read(favoritesControllerProvider).errorMessage;
                ScaffoldMessenger.of(context)
                  ..hideCurrentSnackBar()
                  ..showSnackBar(
                    SnackBar(
                      content: Text(
                        error ??
                            context.l10n.tr(
                              fa:
                                  result
                                      ? 'به علاقه‌مندی‌ها اضافه شد.'
                                      : 'از علاقه‌مندی‌ها حذف شد.',
                              en:
                                  result
                                      ? 'Added to favorites.'
                                      : 'Removed from favorites.',
                            ),
                      ),
                    ),
                  );
              },
      icon:
          isLoading
              ? const SizedBox.square(
                dimension: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
              : Icon(
                isFavorite
                    ? Icons.favorite_rounded
                    : Icons.favorite_border_rounded,
              ),
    );
  }
}
