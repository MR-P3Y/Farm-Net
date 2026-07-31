import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/farm_app_bar.dart';
import '../../farms/data/farm_models.dart';
import '../../farms/data/farm_repository.dart';
import '../../media/data/media_repository.dart';
import '../data/barzegar_api.dart';
import '../data/barzegar_models.dart';
import '../data/barzegar_repository.dart';

class BarzegarScreen extends ConsumerStatefulWidget {
  const BarzegarScreen({super.key});

  @override
  ConsumerState<BarzegarScreen> createState() => _BarzegarScreenState();
}

class _BarzegarScreenState extends ConsumerState<BarzegarScreen> {
  final _messageController = TextEditingController();
  int _tab = 0;
  bool _loading = true;
  bool _sending = false;
  String? _error;
  BarzegarConversation? _conversation;
  BarzegarRequest? _latestRequest;
  BarzegarFeature _feature = barzegarFeatures.first;
  _FarmSelection? _selection;
  PlatformFile? _image;
  List<BarzegarDiarySuggestion> _suggestions = const [];
  List<BarzegarFarmerReport> _reports = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final repository = ref.read(barzegarRepositoryProvider);
      final conversations = await repository.conversations();
      final conversation =
          conversations.isEmpty
              ? await repository.createConversation()
              : await repository.conversation(conversations.first.id);
      final results = await Future.wait([
        repository.diarySuggestions(),
        repository.reports(),
      ]);
      if (!mounted) return;
      setState(() {
        _conversation = conversation;
        _suggestions = results[0] as List<BarzegarDiarySuggestion>;
        _reports = results[1] as List<BarzegarFarmerReport>;
      });
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _send() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _conversation == null || _sending) return;
    if (_feature.contextPurpose != null && _selection == null) {
      await _chooseFarmContext();
      if (_selection == null) return;
    }
    if (_feature.requiresCycle && _selection?.cycle == null) {
      _notice('برای پیشنهاد دفتر، قطعه و چرخه کشت فعال را انتخاب کنید.');
      return;
    }
    if (_feature.requiresImage && _image == null) {
      _notice('ابتدا یک تصویر JPEG، PNG یا WebP انتخاب کنید.');
      return;
    }

    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final repository = ref.read(barzegarRepositoryProvider);
      int? consentId;
      if (_feature.contextPurpose != null) {
        final selection = _selection!;
        final consent = await repository.createConsent(
          farmId: selection.farm.id,
          plotId: selection.plot?.id,
          cycleId: selection.cycle?.id,
          purpose: _feature.contextPurpose!,
        );
        consentId = consent.id;
      }
      String? mediaKey;
      if (_image != null && _feature.requiresImage) {
        final media = await ref
            .read(mediaRepositoryProvider)
            .uploadPlatformFile(
              file: _image!,
              purpose: 'general',
              visibility: 'private',
              altText: 'شاهد تصویری برای تحلیل برزگر',
            );
        mediaKey = media.fileKey;
      }
      final request = await repository.submit(
        conversationId: _conversation!.id,
        content: text,
        feature: _feature,
        contextConsentId: consentId,
        mediaFileKey: mediaKey,
      );
      final conversation = await repository.conversation(_conversation!.id);
      if (!mounted) return;
      setState(() {
        _latestRequest = request;
        _conversation = conversation;
        _messageController.clear();
        _image = null;
      });
      _notice(
        request.isPending
            ? 'درخواست ثبت شد. پس از فعال‌شدن سرویس پردازش، پاسخ آماده می‌شود.'
            : _statusLabel(request.status),
      );
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _refreshRequest() async {
    final current = _latestRequest;
    if (current == null) {
      await _load();
      return;
    }
    try {
      final repository = ref.read(barzegarRepositoryProvider);
      final request = await repository.request(current.id);
      final conversation = await repository.conversation(current.conversationId);
      final suggestions = await repository.diarySuggestions();
      final reports = await repository.reports();
      if (!mounted) return;
      setState(() {
        _latestRequest = request;
        _conversation = conversation;
        _suggestions = suggestions;
        _reports = reports;
      });
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    }
  }

  Future<void> _pickImage() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
      withData: true,
    );
    if (result != null && mounted) {
      setState(() => _image = result.files.single);
    }
  }

  Future<void> _chooseFarmContext() async {
    final selection = await showModalBottomSheet<_FarmSelection>(
      context: context,
      isScrollControlled: true,
      builder: (_) => const _FarmContextSheet(),
    );
    if (selection != null && mounted) {
      setState(() => _selection = selection);
    }
  }

  Future<void> _decide(BarzegarDiarySuggestion item, bool accept) async {
    try {
      await ref
          .read(barzegarRepositoryProvider)
          .decideSuggestion(
            item.id,
            accept: accept,
            reason: accept ? null : 'ردشده توسط کشاورز در اپ',
          );
      await _load();
      if (mounted) {
        _notice(
          accept
              ? 'عملیات با تأیید شما در دفتر مزرعه ثبت شد.'
              : 'پیشنهاد رد شد.',
        );
      }
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    }
  }

  Future<void> _feedback(bool helpful) async {
    final request = _latestRequest;
    if (request == null) return;
    try {
      await ref
          .read(barzegarRepositoryProvider)
          .submitFeedback(request.id, helpful: helpful);
      if (mounted) _notice('بازخورد شما ثبت شد.');
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    }
  }

  Future<void> _deleteConversation() async {
    final conversation = _conversation;
    if (conversation == null) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('حذف گفت‌وگوی برزگر'),
            content: const Text(
              'گفت‌وگو فوراً از فهرست شما پنهان می‌شود و حذف نهایی آن مطابق دوره نگهداری انجام می‌شود.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('درخواست حذف'),
              ),
            ],
          ),
    );
    if (confirmed != true) return;
    try {
      await ref
          .read(barzegarRepositoryProvider)
          .requestConversationDeletion(conversation.id);
      if (!mounted) return;
      setState(() {
        _conversation = null;
        _latestRequest = null;
      });
      await _load();
      if (mounted) _notice('درخواست حذف طبق دوره نگهداری ثبت شد.');
    } catch (error) {
      if (mounted) setState(() => _error = _message(error));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: FarmAppBar(
        title: 'برزگر',
        actions: [
          IconButton(
            tooltip: 'حذف گفت‌وگو',
            onPressed: _conversation == null ? null : _deleteConversation,
            icon: const Icon(Icons.delete_outline_rounded),
          ),
          IconButton(
            tooltip: 'به‌روزرسانی',
            onPressed: _refreshRequest,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: Column(
        children: [
          Material(
            color: Theme.of(context).colorScheme.surfaceContainerLow,
            child: Row(
              children: [
                _TabButton(
                  label: 'گفت‌وگو',
                  selected: _tab == 0,
                  onTap: () => setState(() => _tab = 0),
                ),
                _TabButton(
                  label: 'دفتر هوشمند',
                  selected: _tab == 1,
                  onTap: () => setState(() => _tab = 1),
                ),
                _TabButton(
                  label: 'گزارش‌ها',
                  selected: _tab == 2,
                  onTap: () => setState(() => _tab = 2),
                ),
              ],
            ),
          ),
          if (_error != null)
            MaterialBanner(
              content: Text(_error!),
              actions: [
                TextButton(
                  onPressed: () => setState(() => _error = null),
                  child: const Text('بستن'),
                ),
              ],
            ),
          Expanded(
            child:
                _loading
                    ? const Center(child: CircularProgressIndicator())
                    : switch (_tab) {
                      0 => _chat(),
                      1 => _diary(),
                      _ => _reportList(),
                    },
          ),
        ],
      ),
    );
  }

  Widget _chat() {
    final messages = _conversation?.messages ?? const <BarzegarMessage>[];
    return Column(
      children: [
        Container(
          width: double.infinity,
          margin: const EdgeInsets.fromLTRB(16, 12, 16, 4),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.amber.withValues(alpha: .12),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Text(
            'برزگر توصیه کمکی ارائه می‌کند و جایگزین تشخیص قطعی متخصص نیست. '
            'پردازش زنده تا فعال‌شدن Billing غیرفعال می‌ماند.',
            style: TextStyle(fontSize: 12, height: 1.5),
          ),
        ),
        SizedBox(
          height: 48,
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            scrollDirection: Axis.horizontal,
            itemCount: barzegarFeatures.length,
            separatorBuilder: (_, _) => const SizedBox(width: 8),
            itemBuilder: (_, index) {
              final item = barzegarFeatures[index];
              return ChoiceChip(
                label: Text(item.label),
                selected: item.requestKind == _feature.requestKind,
                onSelected:
                    (_) => setState(() {
                      _feature = item;
                      _selection = null;
                      _image = null;
                    }),
              );
            },
          ),
        ),
        if (_feature.contextPurpose != null)
          ListTile(
            dense: true,
            leading: const Icon(Icons.landscape_outlined),
            title: Text(
              _selection == null
                  ? 'انتخاب مزرعه برای این درخواست'
                  : _selection!.label,
            ),
            trailing: const Icon(Icons.edit_location_alt_outlined),
            onTap: _chooseFarmContext,
          ),
        if (_latestRequest != null)
          Column(
            children: [
              ListTile(
                dense: true,
                leading: Icon(
                  _latestRequest!.isPending
                      ? Icons.schedule_rounded
                      : Icons.task_alt_rounded,
                ),
                title: Text('وضعیت: ${_statusLabel(_latestRequest!.status)}'),
                subtitle:
                    _latestRequest!.failureCode == null
                        ? null
                        : Text(_latestRequest!.failureCode!),
                trailing: IconButton(
                  onPressed: _refreshRequest,
                  icon: const Icon(Icons.sync_rounded),
                ),
              ),
              if (_latestRequest!.status == 'succeeded' ||
                  _latestRequest!.status == 'blocked')
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    TextButton.icon(
                      onPressed: () => _feedback(true),
                      icon: const Icon(Icons.thumb_up_alt_outlined),
                      label: const Text('مفید بود'),
                    ),
                    TextButton.icon(
                      onPressed: () => _feedback(false),
                      icon: const Icon(Icons.thumb_down_alt_outlined),
                      label: const Text('مفید نبود'),
                    ),
                  ],
                ),
            ],
          ),
        Expanded(
          child:
              messages.isEmpty
                  ? const _EmptyState(
                    icon: Icons.auto_awesome_rounded,
                    title: 'از برزگر بپرسید',
                    subtitle:
                        'نوع تحلیل را انتخاب کنید و سؤال کشاورزی خود را بنویسید.',
                  )
                  : ListView.builder(
                    reverse: true,
                    padding: const EdgeInsets.all(16),
                    itemCount: messages.length,
                    itemBuilder: (_, index) {
                      final message = messages[messages.length - 1 - index];
                      return _MessageBubble(message: message);
                    },
                  ),
        ),
        if (_feature.requiresImage)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                TextButton.icon(
                  onPressed: _pickImage,
                  icon: const Icon(Icons.add_photo_alternate_outlined),
                  label: Text(_image?.name ?? 'انتخاب تصویر'),
                ),
                if (_image != null)
                  IconButton(
                    onPressed: () => setState(() => _image = null),
                    icon: const Icon(Icons.close),
                  ),
              ],
            ),
          ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    minLines: 1,
                    maxLines: 5,
                    textInputAction: TextInputAction.newline,
                    decoration: const InputDecoration(
                      hintText: 'سؤال خود را برای برزگر بنویسید…',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  tooltip: 'ارسال',
                  onPressed: _sending ? null : _send,
                  icon:
                      _sending
                          ? const SizedBox.square(
                            dimension: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                          : const Icon(Icons.send_rounded),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _diary() {
    if (_suggestions.isEmpty) {
      return const _EmptyState(
        icon: Icons.menu_book_outlined,
        title: 'پیشنهادی وجود ندارد',
        subtitle:
            'از بخش گفت‌وگو «پیشنهاد دفتر» را انتخاب کنید. ثبت فقط با تأیید شما انجام می‌شود.',
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _suggestions.length,
        itemBuilder: (_, index) {
          final item = _suggestions[index];
          final operation = item.proposedOperation;
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    operation['title']?.toString() ?? 'پیشنهاد عملیات',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${operation['operation_type'] ?? '-'} • '
                    '${operation['occurred_on'] ?? '-'}',
                  ),
                  if (operation['notes'] != null) ...[
                    const SizedBox(height: 8),
                    Text(operation['notes'].toString()),
                  ],
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Chip(label: Text(_statusLabel(item.status))),
                      const Spacer(),
                      if (item.status == 'pending') ...[
                        TextButton(
                          onPressed: () => _decide(item, false),
                          child: const Text('رد'),
                        ),
                        FilledButton(
                          onPressed: () => _decide(item, true),
                          child: const Text('تأیید و ثبت'),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _reportList() {
    if (_reports.isEmpty) {
      return const _EmptyState(
        icon: Icons.summarize_outlined,
        title: 'هنوز گزارشی ساخته نشده',
        subtitle:
            'در گفت‌وگو «گزارش کشاورز» را انتخاب و محدوده مزرعه را مشخص کنید.',
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _reports.length,
        itemBuilder: (_, index) {
          final item = _reports[index];
          final snapshot = item.sourceSnapshot;
          return Card(
            child: ExpansionTile(
              leading: const Icon(Icons.analytics_outlined),
              title: Text('گزارش مزرعه ${item.farmId}'),
              subtitle: Text(
                'عملیات ${snapshot['operation_count'] ?? 0} • '
                'نهاده ${snapshot['input_count'] ?? 0} • '
                'برداشت ${snapshot['harvest_count'] ?? 0}',
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  child: SelectableText(
                    item.narrative,
                    style: const TextStyle(height: 1.7),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _notice(String text) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
  }

  String _message(Object error) {
    if (error is BarzegarApiException) {
      if (error.error.code == 'BILLING_FEATURE_NOT_ENABLED' ||
          error.error.code == 'BILLING_USAGE_LIMIT_EXCEEDED') {
        return 'این قابلیت در اشتراک فعلی فعال نیست یا سهمیه آن تمام شده است.';
      }
      if (error.error.code == 'PERMISSION_DENIED') {
        return 'اجازه استفاده از این قابلیت برای حساب شما فعال نیست.';
      }
      return error.error.message;
    }
    return error.toString();
  }
}

class _FarmContextSheet extends ConsumerStatefulWidget {
  const _FarmContextSheet();

  @override
  ConsumerState<_FarmContextSheet> createState() => _FarmContextSheetState();
}

class _FarmContextSheetState extends ConsumerState<_FarmContextSheet> {
  bool _loading = true;
  List<FarmModel> _farms = const [];
  List<FarmPlotModel> _plots = const [];
  List<CropCycleModel> _cycles = const [];
  FarmModel? _farm;
  FarmPlotModel? _plot;
  CropCycleModel? _cycle;

  @override
  void initState() {
    super.initState();
    _loadFarms();
  }

  Future<void> _loadFarms() async {
    final farms = await ref.read(farmRepositoryProvider).farms();
    if (!mounted) return;
    setState(() {
      _farms = farms.where((item) => item.status == 'active').toList();
      _loading = false;
    });
  }

  Future<void> _selectFarm(FarmModel? farm) async {
    setState(() {
      _farm = farm;
      _plot = null;
      _cycle = null;
      _plots = const [];
      _cycles = const [];
    });
    if (farm == null) return;
    final plots = await ref.read(farmRepositoryProvider).plots(farm.id);
    if (mounted) {
      setState(
        () => _plots = plots.where((item) => item.status == 'active').toList(),
      );
    }
  }

  Future<void> _selectPlot(FarmPlotModel? plot) async {
    setState(() {
      _plot = plot;
      _cycle = null;
      _cycles = const [];
    });
    if (plot == null || _farm == null) return;
    final cycles = await ref
        .read(farmRepositoryProvider)
        .cycles(_farm!.id, plot.id);
    if (mounted) {
      setState(
        () =>
            _cycles =
                cycles.where((item) => item.status != 'cancelled').toList(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          20,
          20,
          20,
          20 + MediaQuery.viewInsetsOf(context).bottom,
        ),
        child:
            _loading
                ? const SizedBox(
                  height: 180,
                  child: Center(child: CircularProgressIndicator()),
                )
                : Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'محدوده‌ای که برزگر اجازه دارد ببیند',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<FarmModel>(
                      initialValue: _farm,
                      decoration: const InputDecoration(labelText: 'مزرعه'),
                      items:
                          _farms
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(item.name),
                                ),
                              )
                              .toList(),
                      onChanged: _selectFarm,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<FarmPlotModel>(
                      initialValue: _plot,
                      decoration: const InputDecoration(
                        labelText: 'قطعه (اختیاری)',
                      ),
                      items:
                          _plots
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(item.name),
                                ),
                              )
                              .toList(),
                      onChanged: _selectPlot,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<CropCycleModel>(
                      initialValue: _cycle,
                      decoration: const InputDecoration(
                        labelText: 'چرخه کشت (اختیاری)',
                      ),
                      items:
                          _cycles
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(item.title ?? 'چرخه ${item.id}'),
                                ),
                              )
                              .toList(),
                      onChanged: (value) => setState(() => _cycle = value),
                    ),
                    const SizedBox(height: 20),
                    FilledButton(
                      onPressed:
                          _farm == null
                              ? null
                              : () => Navigator.pop(
                                context,
                                _FarmSelection(
                                  farm: _farm!,
                                  plot: _plot,
                                  cycle: _cycle,
                                ),
                              ),
                      child: const Text('تأیید دسترسی ۲۴ ساعته'),
                    ),
                  ],
                ),
      ),
    );
  }
}

class _FarmSelection {
  const _FarmSelection({required this.farm, this.plot, this.cycle});
  final FarmModel farm;
  final FarmPlotModel? plot;
  final CropCycleModel? cycle;

  String get label => [
    farm.name,
    if (plot != null) plot!.name,
    if (cycle != null) cycle!.title ?? 'چرخه ${cycle!.id}',
  ].join(' / ');
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});
  final BarzegarMessage message;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 620),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(13),
        decoration: BoxDecoration(
          color:
              message.isUser
                  ? Theme.of(context).colorScheme.primaryContainer
                  : Theme.of(context).colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(18),
        ),
        child: SelectableText(
          message.content,
          style: const TextStyle(height: 1.6),
        ),
      ),
    );
  }
}

class _TabButton extends StatelessWidget {
  const _TabButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: TextButton(
        onPressed: onTap,
        child: Text(
          label,
          style: TextStyle(
            fontWeight: selected ? FontWeight.w900 : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({
    required this.icon,
    required this.title,
    required this.subtitle,
  });
  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 60, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 16),
            Text(title, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(subtitle, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

String _statusLabel(String status) => switch (status) {
  'queued' => 'در صف',
  'running' => 'در حال پردازش',
  'succeeded' => 'آماده',
  'failed' => 'ناموفق',
  'blocked' => 'متوقف‌شده برای ایمنی',
  'cancelled' => 'لغوشده',
  'pending' => 'در انتظار تصمیم شما',
  'accepted' => 'ثبت‌شده',
  'rejected' => 'ردشده',
  _ => status,
};
