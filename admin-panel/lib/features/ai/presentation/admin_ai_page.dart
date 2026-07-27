import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../data/admin_ai_api.dart';
import '../data/admin_ai_models.dart';
import '../data/admin_ai_repository.dart';

class AdminAIPage extends ConsumerStatefulWidget {
  const AdminAIPage({super.key});

  @override
  ConsumerState<AdminAIPage> createState() => _AdminAIPageState();
}

class _AdminAIPageState extends ConsumerState<AdminAIPage> {
  bool _loading = true;
  String? _error;
  int _tab = 0;
  AdminAIOverview? _overview;
  List<AdminAIRequest> _requests = const [];
  List<AdminAIKnowledgeSource> _sources = const [];
  List<AdminAIUsage> _usage = const [];
  List<AdminAIPolicy> _policies = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final repository = ref.read(adminAIRepositoryProvider);
      final values = await Future.wait([
        repository.overview(),
        repository.requests(),
        repository.sources(),
        repository.usage(),
        repository.policies(),
      ]);
      if (!mounted) return;
      setState(() {
        _overview = values[0] as AdminAIOverview;
        _requests = values[1] as List<AdminAIRequest>;
        _sources = values[2] as List<AdminAIKnowledgeSource>;
        _usage = values[3] as List<AdminAIUsage>;
        _policies = values[4] as List<AdminAIPolicy>;
      });
    } catch (error) {
      if (!mounted) return;
      setState(
        () =>
            _error =
                error is AdminAIApiException
                    ? error.error.message
                    : error.toString(),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AdminResponsiveBuilder(
      builder:
          (context, constraints, r) => Padding(
            padding: r.pagePadding(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Text(
                      'حاکمیت برزگر',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const Spacer(),
                    IconButton(
                      tooltip: 'به‌روزرسانی',
                      onPressed: _loading ? null : _load,
                      icon: const Icon(Icons.refresh),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'این پنل فقط metadata عملیاتی را نمایش می‌دهد؛ متن گفت‌وگو و context خصوصی کشاورز پنهان است.',
                ),
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    _error!,
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                ],
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: [
                    for (final entry in const [
                      'نمای کلی',
                      'اجراها',
                      'دانش',
                      'مصرف',
                      'سیاست‌ها',
                    ].indexed)
                      ChoiceChip(
                        label: Text(entry.$2),
                        selected: _tab == entry.$1,
                        onSelected: (_) => setState(() => _tab = entry.$1),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child:
                      _loading
                          ? const Center(child: CircularProgressIndicator())
                          : switch (_tab) {
                            0 => _overviewView(),
                            1 => _requestsView(),
                            2 => _sourcesView(),
                            3 => _usageView(),
                            _ => _policiesView(),
                          },
                ),
              ],
            ),
          ),
    );
  }

  Widget _overviewView() {
    final item = _overview;
    if (item == null) return const Center(child: Text('داده‌ای وجود ندارد.'));
    final cards = <(String, String, IconData)>[
      ('کل درخواست‌ها', '${item.totalRequests}', Icons.auto_awesome),
      ('موفق', '${item.succeededRequests}', Icons.check_circle_outline),
      ('در صف/اجرا', '${item.queuedRequests + item.runningRequests}', Icons.schedule),
      ('مسدود ایمنی', '${item.blockedRequests}', Icons.health_and_safety_outlined),
      ('بازخورد منفی', '${item.negativeFeedback}', Icons.thumb_down_alt_outlined),
      ('منابع منتظر', '${item.pendingKnowledgeSources}', Icons.library_books_outlined),
      ('مغایرت مصرف', '${item.reconciliationIssues}', Icons.rule_outlined),
      (
        'هزینه Provider',
        '${item.totalProviderCostToman.toStringAsFixed(0)} تومان',
        Icons.payments_outlined,
      ),
    ];
    return GridView.extent(
      maxCrossAxisExtent: 270,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.8,
      children:
          cards
              .map(
                (card) => Card(
                  child: ListTile(
                    leading: Icon(card.$3),
                    title: Text(card.$1),
                    subtitle: Text(
                      card.$2,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                ),
              )
              .toList(),
    );
  }

  Widget _requestsView() => _listOrEmpty(
    _requests,
    (item) => Card(
      child: ListTile(
        leading: _StatusIcon(item.status),
        title: Text('#${item.id} • ${item.requestKind}'),
        subtitle: Text(
          'کاربر ${item.userId} • ${item.featureCode} • تلاش ${item.attemptCount}\n'
          '${item.failureCode ?? item.safetyCode ?? 'بدون خطای ثبت‌شده'}',
        ),
        trailing: Chip(label: Text(item.status)),
      ),
    ),
  );

  Widget _sourcesView() => Column(
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: FilledButton.icon(
          onPressed: _createSource,
          icon: const Icon(Icons.add),
          label: const Text('منبع جدید'),
        ),
      ),
      const SizedBox(height: 8),
      Expanded(
        child: _listOrEmpty(
          _sources,
          (item) => Card(
            child: ListTile(
              title: Text(item.title),
              subtitle: Text(
                '${item.publisher} • ${item.licenseCode}\n${item.code}',
              ),
              trailing: Wrap(
                spacing: 6,
                children: [
                  Chip(label: Text(item.status)),
                  if (item.status == 'draft')
                    TextButton(
                      onPressed: () => _submitSource(item.id),
                      child: const Text('ارسال بررسی'),
                    ),
                  if (item.status == 'in_review') ...[
                    TextButton(
                      onPressed: () => _review(item.id, 'rejected'),
                      child: const Text('رد'),
                    ),
                    FilledButton(
                      onPressed: () => _review(item.id, 'approved'),
                      child: const Text('تأیید'),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    ],
  );

  Widget _usageView() => _listOrEmpty(
    _usage,
    (item) => Card(
      child: ListTile(
        title: Text('${item.provider} / ${item.model}'),
        subtitle: Text(
          'درخواست ${item.requestId} • ورودی ${item.inputTokens} • خروجی ${item.outputTokens} '
          '• ${item.latencyMs}ms',
        ),
        trailing: Text(
          item.costToman == null
              ? 'نرخ ثبت نشده'
              : '${item.costToman!.toStringAsFixed(2)} تومان',
        ),
      ),
    ),
  );

  Widget _policiesView() => _listOrEmpty(
    _policies,
    (item) => Card(
      child: ListTile(
        title: Text('${item.key} • ${item.version}'),
        subtitle: Text(item.requestKind),
        trailing: Chip(label: Text(item.status)),
      ),
    ),
  );

  Widget _listOrEmpty<T>(List<T> items, Widget Function(T) builder) {
    if (items.isEmpty) return const Center(child: Text('موردی برای نمایش وجود ندارد.'));
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (_, index) => builder(items[index]),
    );
  }

  Future<void> _createSource() async {
    final code = TextEditingController();
    final title = TextEditingController();
    final publisher = TextEditingController();
    final license = TextEditingController();
    final evidence = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('منبع دانش جدید'),
            content: SizedBox(
              width: 520,
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    for (final field in [
                      (code, 'کد انگلیسی'),
                      (title, 'عنوان'),
                      (publisher, 'ناشر'),
                      (license, 'کد مجوز'),
                      (evidence, 'مدرک/شرح مجوز'),
                    ])
                      Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: TextField(
                          controller: field.$1,
                          decoration: InputDecoration(
                            labelText: field.$2,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('ایجاد پیش‌نویس'),
              ),
            ],
          ),
    );
    if (accepted != true) return;
    try {
      await ref.read(adminAIRepositoryProvider).createSource({
        'code': code.text.trim(),
        'title': title.text.trim(),
        'publisher': publisher.text.trim(),
        'license_code': license.text.trim(),
        'license_evidence': evidence.text.trim(),
      });
      await _load();
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    }
  }

  Future<void> _submitSource(int id) async {
    await ref.read(adminAIRepositoryProvider).submitSource(id);
    await _load();
  }

  Future<void> _review(int id, String decision) async {
    final reason = TextEditingController();
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(decision == 'approved' ? 'تأیید منبع' : 'رد منبع'),
            content: TextField(
              controller: reason,
              minLines: 2,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'دلیل تصمیم',
                border: OutlineInputBorder(),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('ثبت تصمیم'),
              ),
            ],
          ),
    );
    if (accepted != true || reason.text.trim().length < 3) return;
    await ref
        .read(adminAIRepositoryProvider)
        .reviewSource(id, decision: decision, reason: reason.text.trim());
    await _load();
  }
}

class _StatusIcon extends StatelessWidget {
  const _StatusIcon(this.status);
  final String status;
  @override
  Widget build(BuildContext context) => Icon(
    status == 'blocked'
        ? Icons.health_and_safety_outlined
        : status == 'succeeded'
        ? Icons.check_circle_outline
        : status == 'failed'
        ? Icons.error_outline
        : Icons.schedule,
  );
}
