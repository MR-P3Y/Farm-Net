import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/admin_auth_state.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_error_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_subscription_api.dart';
import '../data/admin_subscription_models.dart';
import '../data/admin_subscription_repository.dart';

class AdminSubscriptionsPage extends ConsumerStatefulWidget {
  const AdminSubscriptionsPage({super.key});

  @override
  ConsumerState<AdminSubscriptionsPage> createState() =>
      _AdminSubscriptionsPageState();
}

class _AdminSubscriptionsPageState extends ConsumerState<AdminSubscriptionsPage>
    with SingleTickerProviderStateMixin {
  final _repository = AdminSubscriptionRepository();
  final _search = TextEditingController();
  late final TabController _tabs;
  AdminBillingPage<AdminBillingPlan>? _plans;
  AdminBillingPage<AdminBillingSubscription>? _subscriptions;
  String? _status;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this)..addListener(() {
      if (!_tabs.indexIsChanging) {
        _status = null;
        _search.clear();
        _load(1);
      }
    });
    _load(1);
  }

  @override
  void dispose() {
    _tabs.dispose();
    _search.dispose();
    super.dispose();
  }

  Future<void> _load(int page) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      if (_tabs.index == 0) {
        _plans = await _repository.plans(
          query: _search.text.trim(),
          status: _status,
          page: page,
        );
      } else {
        _subscriptions = await _repository.subscriptions(
          query: _search.text.trim(),
          status: _status,
          page: page,
        );
      }
    } on AdminSubscriptionApiException catch (error) {
      _error = error.error.message;
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _planStatus(AdminBillingPlan plan, String status) async {
    try {
      await _repository.setPlanStatus(plan, status);
      await _load(_plans?.page ?? 1);
    } on AdminSubscriptionApiException catch (error) {
      _showError(error.error.message);
    }
  }

  Future<void> _createPlan() async {
    final templates = _plans?.items ?? const <AdminBillingPlan>[];
    if (templates.isEmpty) {
      _showError(
        'برای ساخت نخستین نسخه، کاتالوگ قابلیت‌ها باید Seed شده باشد.',
      );
      return;
    }
    final payload = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (_) => _PlanDialog(templates: templates),
    );
    if (payload == null) return;
    try {
      await _repository.createPlan(payload);
      await _load(1);
    } on AdminSubscriptionApiException catch (error) {
      _showError(error.error.message);
    }
  }

  Future<void> _manualActivate() async {
    final activePlans =
        (_plans?.items ?? const <AdminBillingPlan>[])
            .where((plan) => plan.status == 'active')
            .toList();
    if (activePlans.isEmpty) {
      final result = await _repository.plans(status: 'active');
      activePlans.addAll(result.items);
    }
    if (!mounted) return;
    if (activePlans.isEmpty) {
      _showError('هیچ پلن فعالی برای تخصیص وجود ندارد.');
      return;
    }
    final value = await showDialog<_ManualActivation>(
      context: context,
      builder: (_) => _ManualActivationDialog(plans: activePlans),
    );
    if (value == null) return;
    try {
      await _repository.manualActivate(
        userId: value.userId,
        planId: value.planId,
        reason: value.reason,
      );
      await _load(1);
    } on AdminSubscriptionApiException catch (error) {
      _showError(error.error.message);
    }
  }

  Future<void> _showDetail(AdminBillingSubscription summary) async {
    try {
      final detail = await _repository.subscription(summary.id);
      if (!mounted) return;
      await showDialog<void>(
        context: context,
        builder: (_) => _SubscriptionDetailDialog(subscription: detail),
      );
    } on AdminSubscriptionApiException catch (error) {
      _showError(error.error.message);
    }
  }

  Future<void> _cancel(AdminBillingSubscription summary) async {
    final detail = await _repository.subscription(summary.id);
    if (!mounted) return;
    final value = await showDialog<_Cancellation>(
      context: context,
      builder: (_) => const _CancellationDialog(),
    );
    if (value == null) return;
    try {
      await _repository.cancel(
        subscription: detail,
        reason: value.reason,
        atPeriodEnd: value.atPeriodEnd,
      );
      await _load(_subscriptions?.page ?? 1);
    } on AdminSubscriptionApiException catch (error) {
      _showError(error.error.message);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red.shade700),
    );
  }

  bool _can(String permission) =>
      ref.read(adminAuthStateProvider).hasPermission(permission);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('پلن‌ها و اشتراک‌ها'),
        bottom: TabBar(
          controller: _tabs,
          tabs: const [Tab(text: 'پلن‌ها'), Tab(text: 'اشتراک کاربران')],
        ),
        actions: [
          if (_tabs.index == 0 && _can('billing.plans.create'))
            TextButton.icon(
              onPressed: _createPlan,
              icon: const Icon(Icons.add),
              label: const Text('نسخه جدید'),
            ),
          if (_tabs.index == 1 && _can('billing.subscriptions.activate'))
            TextButton.icon(
              onPressed: _manualActivate,
              icon: const Icon(Icons.card_membership),
              label: const Text('فعال‌سازی دستی'),
            ),
        ],
      ),
      body: Column(
        children: [
          _filters(),
          Expanded(
            child:
                _loading
                    ? const AdminLoadingView()
                    : _error != null
                    ? AdminErrorView(message: _error!, onRetry: () => _load(1))
                    : _tabs.index == 0
                    ? _planTable()
                    : _subscriptionTable(),
          ),
        ],
      ),
    );
  }

  Widget _filters() {
    final statuses =
        _tabs.index == 0
            ? const ['draft', 'active', 'retired']
            : const ['pending', 'active', 'grace', 'cancelled', 'expired'];
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          SizedBox(
            width: 280,
            child: TextField(
              controller: _search,
              decoration: InputDecoration(
                labelText:
                    _tabs.index == 0
                        ? 'جستجوی نام یا کد پلن'
                        : 'ایمیل یا موبایل کاربر',
                prefixIcon: const Icon(Icons.search),
              ),
              onSubmitted: (_) => _load(1),
            ),
          ),
          DropdownButton<String?>(
            value: _status,
            hint: const Text('همه وضعیت‌ها'),
            items: [
              const DropdownMenuItem<String?>(
                value: null,
                child: Text('همه وضعیت‌ها'),
              ),
              for (final status in statuses)
                DropdownMenuItem(value: status, child: Text(status)),
            ],
            onChanged: (value) {
              setState(() => _status = value);
              _load(1);
            },
          ),
          IconButton(
            onPressed: () => _load(1),
            tooltip: 'بازخوانی',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
    );
  }

  Widget _planTable() {
    final result = _plans;
    if (result == null || result.items.isEmpty) {
      return const AdminEmptyView(message: 'پلنی یافت نشد.');
    }
    return _paged(
      result.page,
      result.totalPages,
      result.total,
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          columns: const [
            DataColumn(label: Text('کد / نسخه')),
            DataColumn(label: Text('نام')),
            DataColumn(label: Text('دوره')),
            DataColumn(label: Text('قیمت (تومان)')),
            DataColumn(label: Text('قابلیت‌ها')),
            DataColumn(label: Text('وضعیت')),
            DataColumn(label: Text('عملیات')),
          ],
          rows: [
            for (final plan in result.items)
              DataRow(
                cells: [
                  DataCell(Text('${plan.code} / v${plan.version}')),
                  DataCell(Text(plan.name)),
                  DataCell(Text(plan.billingPeriod)),
                  DataCell(Text(_money(plan.priceToman))),
                  DataCell(Text('${plan.features.length}')),
                  DataCell(Text(plan.status)),
                  DataCell(
                    Wrap(
                      children: [
                        if (plan.status == 'draft' &&
                            _can('billing.plans.update'))
                          TextButton(
                            onPressed: () => _planStatus(plan, 'active'),
                            child: const Text('فعال‌سازی'),
                          ),
                        if (!plan.isDefaultFree &&
                            plan.status != 'retired' &&
                            _can('billing.plans.update'))
                          TextButton(
                            onPressed: () => _planStatus(plan, 'retired'),
                            child: const Text('بازنشسته'),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _subscriptionTable() {
    final result = _subscriptions;
    if (result == null || result.items.isEmpty) {
      return const AdminEmptyView(message: 'اشتراکی یافت نشد.');
    }
    return _paged(
      result.page,
      result.totalPages,
      result.total,
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          columns: const [
            DataColumn(label: Text('کاربر')),
            DataColumn(label: Text('پلن')),
            DataColumn(label: Text('وضعیت')),
            DataColumn(label: Text('پایان دوره')),
            DataColumn(label: Text('منبع')),
            DataColumn(label: Text('عملیات')),
          ],
          rows: [
            for (final item in result.items)
              DataRow(
                onSelectChanged: (_) => _showDetail(item),
                cells: [
                  DataCell(Text('${item.userLabel}\n#${item.userId}')),
                  DataCell(Text(item.planName)),
                  DataCell(Text(item.status)),
                  DataCell(Text(_date(item.periodEndsAt))),
                  DataCell(Text(item.activationSource)),
                  DataCell(
                    Wrap(
                      children: [
                        TextButton(
                          onPressed: () => _showDetail(item),
                          child: const Text('جزئیات/مصرف'),
                        ),
                        if ({'active', 'grace'}.contains(item.status) &&
                            _can('billing.subscriptions.cancel'))
                          TextButton(
                            onPressed: () => _cancel(item),
                            child: const Text('لغو'),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _paged(int page, int totalPages, int total, Widget child) {
    return Column(
      children: [
        Expanded(child: SingleChildScrollView(child: child)),
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed: page > 1 ? () => _load(page - 1) : null,
                icon: const Icon(Icons.chevron_right),
              ),
              Text('صفحه $page از $totalPages — $total رکورد'),
              IconButton(
                onPressed: page < totalPages ? () => _load(page + 1) : null,
                icon: const Icon(Icons.chevron_left),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _PlanDialog extends StatefulWidget {
  const _PlanDialog({required this.templates});
  final List<AdminBillingPlan> templates;

  @override
  State<_PlanDialog> createState() => _PlanDialogState();
}

class _PlanDialogState extends State<_PlanDialog> {
  late AdminBillingPlan _template = widget.templates.first;
  late final _code = TextEditingController(text: _template.code);
  late final _name = TextEditingController(text: _template.name);
  late final _price = TextEditingController(
    text: _template.priceToman.toString(),
  );
  late String _period = _template.billingPeriod;

  void _select(AdminBillingPlan plan) {
    setState(() {
      _template = plan;
      _code.text = plan.code;
      _name.text = plan.name;
      _price.text = plan.priceToman.toString();
      _period = plan.billingPeriod;
    });
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('ساخت نسخه Draft از روی الگو'),
      content: SizedBox(
        width: 560,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<AdminBillingPlan>(
                initialValue: _template,
                decoration: const InputDecoration(labelText: 'الگوی قابلیت‌ها'),
                items: [
                  for (final plan in widget.templates)
                    DropdownMenuItem(
                      value: plan,
                      child: Text(
                        '${plan.name} — ${plan.code} v${plan.version}',
                      ),
                    ),
                ],
                onChanged: (value) {
                  if (value != null) _select(value);
                },
              ),
              TextField(
                controller: _code,
                decoration: const InputDecoration(
                  labelText: 'کد پلن (برای خانواده جدید تغییر دهید)',
                ),
              ),
              TextField(
                controller: _name,
                decoration: const InputDecoration(labelText: 'نام'),
              ),
              DropdownButtonFormField<String>(
                initialValue: _period,
                decoration: const InputDecoration(labelText: 'دوره'),
                items: const [
                  DropdownMenuItem(value: 'free', child: Text('رایگان')),
                  DropdownMenuItem(value: 'monthly', child: Text('ماهانه')),
                  DropdownMenuItem(value: 'yearly', child: Text('سالانه')),
                ],
                onChanged: (value) => setState(() => _period = value!),
              ),
              TextField(
                controller: _price,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'قیمت تومان'),
              ),
              const SizedBox(height: 12),
              Text(
                '${_template.features.length} قابلیت از الگو کپی می‌شود؛ '
                'نسخه فعال مستقیماً تغییر نمی‌کند.',
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('انصراف'),
        ),
        FilledButton(
          onPressed: () {
            final price = num.tryParse(_price.text);
            if (_code.text.trim().length < 2 ||
                _name.text.trim().length < 2 ||
                price == null ||
                (_period == 'free' && price != 0)) {
              return;
            }
            Navigator.pop(context, {
              'code': _code.text.trim(),
              'name': _name.text.trim(),
              'description': _template.description,
              'billing_period': _period,
              'price_toman': price,
              'features':
                  _template.features.map((item) => item.toInput()).toList(),
            });
          },
          child: const Text('ساخت Draft'),
        ),
      ],
    );
  }
}

class _ManualActivation {
  const _ManualActivation(this.userId, this.planId, this.reason);
  final int userId;
  final int planId;
  final String reason;
}

class _ManualActivationDialog extends StatefulWidget {
  const _ManualActivationDialog({required this.plans});
  final List<AdminBillingPlan> plans;

  @override
  State<_ManualActivationDialog> createState() =>
      _ManualActivationDialogState();
}

class _ManualActivationDialogState extends State<_ManualActivationDialog> {
  final _userId = TextEditingController();
  final _reason = TextEditingController();
  late int _planId = widget.plans.first.id;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('فعال‌سازی دستی اشتراک'),
      content: SizedBox(
        width: 480,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _userId,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'شناسه کاربر'),
            ),
            DropdownButtonFormField<int>(
              initialValue: _planId,
              decoration: const InputDecoration(labelText: 'پلن فعال'),
              items: [
                for (final plan in widget.plans)
                  DropdownMenuItem(
                    value: plan.id,
                    child: Text(
                      '${plan.name} — ${_money(plan.priceToman)} تومان',
                    ),
                  ),
              ],
              onChanged: (value) => _planId = value!,
            ),
            TextField(
              controller: _reason,
              maxLength: 500,
              decoration: const InputDecoration(
                labelText: 'دلیل اجباری و قابل ممیزی',
              ),
            ),
            const Text(
              'این عملیات پرداخت یا فاکتور جعلی ایجاد نمی‌کند و با منبع admin ثبت می‌شود.',
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('انصراف'),
        ),
        FilledButton(
          onPressed: () {
            final userId = int.tryParse(_userId.text);
            if (userId == null || _reason.text.trim().length < 3) return;
            Navigator.pop(
              context,
              _ManualActivation(userId, _planId, _reason.text.trim()),
            );
          },
          child: const Text('فعال‌سازی'),
        ),
      ],
    );
  }
}

class _Cancellation {
  const _Cancellation(this.reason, this.atPeriodEnd);
  final String reason;
  final bool atPeriodEnd;
}

class _CancellationDialog extends StatefulWidget {
  const _CancellationDialog();

  @override
  State<_CancellationDialog> createState() => _CancellationDialogState();
}

class _CancellationDialogState extends State<_CancellationDialog> {
  final _reason = TextEditingController();
  bool _atPeriodEnd = true;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('لغو اشتراک'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SwitchListTile(
            value: _atPeriodEnd,
            onChanged: (value) => setState(() => _atPeriodEnd = value),
            title: const Text('لغو در پایان دوره'),
            subtitle: const Text('خاموش: قطع دسترسی فوری'),
          ),
          TextField(
            controller: _reason,
            maxLength: 500,
            decoration: const InputDecoration(labelText: 'دلیل اجباری'),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('انصراف'),
        ),
        FilledButton(
          onPressed: () {
            if (_reason.text.trim().length < 3) return;
            Navigator.pop(
              context,
              _Cancellation(_reason.text.trim(), _atPeriodEnd),
            );
          },
          child: const Text('ثبت لغو'),
        ),
      ],
    );
  }
}

class _SubscriptionDetailDialog extends StatelessWidget {
  const _SubscriptionDetailDialog({required this.subscription});
  final AdminBillingSubscription subscription;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('اشتراک #${subscription.id} — ${subscription.userLabel}'),
      content: SizedBox(
        width: 700,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('پلن: ${subscription.planName} (${subscription.planCode})'),
              Text('وضعیت: ${subscription.status}'),
              Text('قیمت: ${_money(subscription.priceToman)} تومان'),
              Text('پایان دوره: ${_date(subscription.periodEndsAt)}'),
              Text('منبع فعال‌سازی: ${subscription.activationSource}'),
              if (subscription.activationReason != null)
                Text('دلیل فعال‌سازی: ${subscription.activationReason}'),
              if (subscription.cancellationReason != null)
                Text('دلیل لغو: ${subscription.cancellationReason}'),
              const Divider(),
              const Text(
                'مصرف قابلیت‌ها',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              if (subscription.usage.isEmpty)
                const Text('مصرف اندازه‌گیری‌شده‌ای وجود ندارد.')
              else
                DataTable(
                  columns: const [
                    DataColumn(label: Text('قابلیت')),
                    DataColumn(label: Text('مصرف')),
                    DataColumn(label: Text('رزرو')),
                    DataColumn(label: Text('باقی‌مانده')),
                  ],
                  rows: [
                    for (final usage in subscription.usage)
                      DataRow(
                        cells: [
                          DataCell(Text(usage.code)),
                          DataCell(Text('${usage.used}')),
                          DataCell(Text('${usage.reserved}')),
                          DataCell(
                            Text(
                              usage.unlimited
                                  ? 'نامحدود'
                                  : '${usage.remaining ?? '-'}',
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('بستن'),
        ),
      ],
    );
  }
}

String _money(num value) {
  final digits = value.round().toString();
  return digits.replaceAllMapped(
    RegExp(r'(?<=\d)(?=(\d{3})+(?!\d))'),
    (_) => '٬',
  );
}

String _date(DateTime? value) =>
    value == null ? '-' : value.toLocal().toString().split('.').first;
