import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../data/media_models.dart';
import '../state/media_controller.dart';

class MediaUploadButton extends ConsumerWidget {
  const MediaUploadButton({
    required this.label,
    required this.purpose,
    required this.visibility,
    required this.onUploaded,
    this.icon = Icons.upload_file_outlined,
    this.altText,
    this.description,
    this.allowedExtensions = const ['jpg', 'jpeg', 'png', 'webp', 'pdf'],
    super.key,
  });

  final String label;
  final IconData icon;
  final String purpose;
  final String visibility;
  final String? altText;
  final String? description;
  final List<String> allowedExtensions;
  final ValueChanged<MediaFileModel> onUploaded;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(mediaControllerProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        OutlinedButton.icon(
          onPressed:
              state.isUploading
                  ? null
                  : () async {
                    final uploaded = await ref
                        .read(mediaControllerProvider.notifier)
                        .pickAndUpload(
                          purpose: purpose,
                          visibility: visibility,
                          altText: altText,
                          description: description,
                          fileType: FileType.custom,
                          allowedExtensions: allowedExtensions,
                        );

                    if (uploaded == null) return;
                    onUploaded(uploaded);

                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          context.l10n.tr(
                            fa: 'فایل با موفقیت بارگذاری شد.',
                            en: 'File uploaded successfully.',
                          ),
                        ),
                      ),
                    );
                  },
          icon: Icon(icon),
          label: Text(
            state.isUploading
                ? context.l10n.tr(fa: 'در حال بارگذاری...', en: 'Uploading...')
                : label,
          ),
        ),
        if (state.errorMessage != null) ...[
          const SizedBox(height: 8),
          Text(
            state.errorMessage!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
      ],
    );
  }
}
