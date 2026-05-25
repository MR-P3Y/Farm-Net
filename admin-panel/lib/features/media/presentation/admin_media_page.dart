import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/admin_config.dart';
import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_media_models.dart';
import '../state/admin_media_controller.dart';

class AdminMediaPage extends ConsumerStatefulWidget {
  const AdminMediaPage({super.key});

  @override
  ConsumerState<AdminMediaPage> createState() => _AdminMediaPageState();
}

class _AdminMediaPageState extends ConsumerState<AdminMediaPage> {
  bool _loaded = false;
  String? _purposeFilter;
  String? _visibilityFilter;
  String? _statusFilter;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminMediaControllerProvider.notifier).load();
    });
  }

  Future<void> _reload() {
    return ref
        .read(adminMediaControllerProvider.notifier)
        .load(
          purpose: _purposeFilter,
          visibility: _visibilityFilter,
          status: _statusFilter,
        );
  }

  Future<void> _openDetail(AdminMediaFile item) async {
    await ref
        .read(adminMediaControllerProvider.notifier)
        .loadDetail(item.fileKey);

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) => _MediaDetailDialog(fileKey: item.fileKey),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminMediaControllerProvider);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return Padding(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Text(
                    'مدیریت فایل‌ها',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Refresh',
                    onPressed: _reload,
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  SizedBox(
                    width: r.isCompact ? double.infinity : 280,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _purposeFilter,
                      decoration: const InputDecoration(
                        labelText: 'Purpose',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'product_image',
                          child: Text('product_image'),
                        ),
                        DropdownMenuItem(
                          value: 'store_logo',
                          child: Text('store_logo'),
                        ),
                        DropdownMenuItem(
                          value: 'store_banner',
                          child: Text('store_banner'),
                        ),
                        DropdownMenuItem(
                          value: 'profile_document',
                          child: Text('profile_document'),
                        ),
                        DropdownMenuItem(
                          value: 'verification_document',
                          child: Text('verification_document'),
                        ),
                        DropdownMenuItem(
                          value: 'general',
                          child: Text('general'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _purposeFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 220,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _visibilityFilter,
                      decoration: const InputDecoration(
                        labelText: 'Visibility',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'public',
                          child: Text('public'),
                        ),
                        DropdownMenuItem(
                          value: 'private',
                          child: Text('private'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _visibilityFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                  SizedBox(
                    width: r.isCompact ? double.infinity : 220,
                    child: DropdownButtonFormField<String?>(
                      initialValue: _statusFilter,
                      decoration: const InputDecoration(
                        labelText: 'Status',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem<String?>(
                          value: null,
                          child: Text('همه'),
                        ),
                        DropdownMenuItem(
                          value: 'active',
                          child: Text('active'),
                        ),
                        DropdownMenuItem(
                          value: 'deleted',
                          child: Text('deleted'),
                        ),
                        DropdownMenuItem(
                          value: 'quarantined',
                          child: Text('quarantined'),
                        ),
                      ],
                      onChanged: (value) async {
                        setState(() => _statusFilter = value);
                        await _reload();
                      },
                    ),
                  ),
                ],
              ),
              if (state.errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(
                  state.errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
              const SizedBox(height: 16),
              Expanded(
                child:
                    state.isLoading
                        ? const AdminLoadingView()
                        : _MediaTable(items: state.items, onOpen: _openDetail),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _MediaTable extends StatelessWidget {
  const _MediaTable({required this.items, required this.onOpen});

  final List<AdminMediaFile> items;
  final ValueChanged<AdminMediaFile> onOpen;

  String _sizeText(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const AdminEmptyView(message: 'فایلی برای نمایش وجود ندارد.');
    }

    return SingleChildScrollView(
      child: AdminDataTable(
        columns: const [
          DataColumn(label: Text('ID')),
          DataColumn(label: Text('Filename')),
          DataColumn(label: Text('Purpose')),
          DataColumn(label: Text('Visibility')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Size')),
          DataColumn(label: Text('Action')),
        ],
        rows:
            items.map((item) {
              return DataRow(
                cells: [
                  DataCell(Text(item.id.toString())),
                  DataCell(Text(item.originalFilename)),
                  DataCell(Text(item.purpose)),
                  DataCell(Text(item.visibility)),
                  DataCell(Text(item.status)),
                  DataCell(Text(_sizeText(item.sizeBytes))),
                  DataCell(
                    TextButton(
                      onPressed: () => onOpen(item),
                      child: const Text('جزئیات'),
                    ),
                  ),
                ],
              );
            }).toList(),
      ),
    );
  }
}

class _MediaDetailDialog extends ConsumerStatefulWidget {
  const _MediaDetailDialog({required this.fileKey});

  final String fileKey;

  @override
  ConsumerState<_MediaDetailDialog> createState() => _MediaDetailDialogState();
}

class _MediaDetailDialogState extends ConsumerState<_MediaDetailDialog> {
  final _descriptionController = TextEditingController();
  String? _filledForFileKey;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  String _absoluteUrl(String path) {
    final base = AdminConfig.apiBaseUrl.replaceFirst('/api/v1', '');
    return '$base$path';
  }

  Future<void> _update(String status) async {
    final ok = await ref
        .read(adminMediaControllerProvider.notifier)
        .updateStatus(
          fileKey: widget.fileKey,
          status: status,
          description: _descriptionController.text.trim(),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminMediaControllerProvider);
    final item = state.selected;

    if (item == null) {
      return const AlertDialog(
        content: SizedBox(height: 120, child: AdminLoadingView()),
      );
    }

    if (_filledForFileKey != item.fileKey) {
      _filledForFileKey = item.fileKey;
      _descriptionController.text = item.description ?? '';
    }

    final publicUrl = _absoluteUrl(item.publicPath);
    final privateUrl = _absoluteUrl(item.privatePath);
    final adminPrivateUrl = _absoluteUrl(item.adminPrivatePath);
    final accessUrl = item.visibility == 'public' ? publicUrl : adminPrivateUrl;

    return AlertDialog(
      title: Text('فایل #${item.id}'),
      content: SizedBox(
        width: 780,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.72,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _DetailLine(label: 'File key', value: item.fileKey),
                _DetailLine(label: 'Filename', value: item.originalFilename),
                _DetailLine(
                  label: 'Owner',
                  value: '${item.ownerUserId ?? '-'}',
                ),
                _DetailLine(label: 'Purpose', value: item.purpose),
                _DetailLine(label: 'Visibility', value: item.visibility),
                _DetailLine(label: 'Status', value: item.status),
                _DetailLine(label: 'MIME', value: item.mimeType),
                _DetailLine(label: 'Size', value: '${item.sizeBytes} bytes'),
                _DetailLine(label: 'Path', value: item.relativePath),
                const Divider(height: 28),
                SelectableText('Public URL:\n$publicUrl'),
                const SizedBox(height: 8),
                SelectableText('Private URL:\n$privateUrl'),
                const SizedBox(height: 8),
                SelectableText('Admin private URL:\n$adminPrivateUrl'),
                const SizedBox(height: 16),
                if (item.mimeType.startsWith('image/') &&
                    item.status == 'active' &&
                    item.visibility == 'public')
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      accessUrl,
                      height: 220,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) {
                        return const Padding(
                          padding: EdgeInsets.all(16),
                          child: Text('Preview failed'),
                        );
                      },
                    ),
                  ),
                const SizedBox(height: 16),
                TextField(
                  controller: _descriptionController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'توضیحات / دلیل مدیریت',
                    border: OutlineInputBorder(),
                  ),
                ),
                if (state.errorMessage != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: state.isSaving ? null : () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
        OutlinedButton.icon(
          onPressed: state.isSaving ? null : () => _update('quarantined'),
          icon: const Icon(Icons.block_outlined),
          label: const Text('Quarantine'),
        ),
        OutlinedButton.icon(
          onPressed: state.isSaving ? null : () => _update('deleted'),
          icon: const Icon(Icons.delete_outline),
          label: const Text('Delete'),
        ),
        FilledButton.icon(
          onPressed: state.isSaving ? null : () => _update('active'),
          icon: const Icon(Icons.check_circle_outline),
          label: const Text('Active'),
        ),
      ],
    );
  }
}

class _DetailLine extends StatelessWidget {
  const _DetailLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 140, child: Text(label)),
          Expanded(child: SelectableText(value)),
        ],
      ),
    );
  }
}
