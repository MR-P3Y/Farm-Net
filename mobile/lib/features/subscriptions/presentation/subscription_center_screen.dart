import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/app_config.dart';
import '../../../core/utils/money.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../data/subscription_models.dart';
import '../state/subscription_controller.dart';

class SubscriptionCenterScreen extends ConsumerStatefulWidget {
  const SubscriptionCenterScreen({super.key});

  @override
  ConsumerState<SubscriptionCenterScreen> createState() =>
      _SubscriptionCenterScreenState();
}

class _SubscriptionCenterScreenState
    extends ConsumerState<SubscriptionCenterScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(subscriptionControllerProvider.notifier).load(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(subscriptionControllerProvider);
    return Scaffold(
      appBar: const FarmAppBar(title: 'اشتراک و امکانات من'),
      body: RefreshIndicator(
        onRefresh:
            () => ref.read(subscriptionControllerProvider.notifier).load(),
        child:
            state.loading && state.plans.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    if (state.error != null) _errorCard(context, state.error!),
                    _currentCard(context, state),
                    const SizedBox(height: 20),
                    Text(
                      'میزان مصرف این دوره',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    _usage(context, state.usage),
                    const SizedBox(height: 20),
                    Text(
                      'پلن‌های فارم‌نت',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    if (state.plans.isEmpty)
                      const Card(
                        child: Padding(
                          padding: EdgeInsets.all(20),
                          child: Text(
                            'در حال حاضر پلنی برای نمایش وجود ندارد.',
                          ),
                        ),
                      )
                    else
                      ...state.plans.map(
                        (plan) => _planCard(context, state, plan),
                      ),
                    const SizedBox(height: 24),
                    const Text(
                      'تمام قیمت‌ها به تومان ایران هستند. نقش‌ها و تأیید حرفه‌ای با خرید اشتراک تغییر نمی‌کنند.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
      ),
    );
  }

  Widget _currentCard(BuildContext context, SubscriptionState state) {
    final current = state.current;
    if (current == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'اشتراک فعالی ندارید',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              const Text('برای شروع می‌توانید پلن رایگان را فعال کنید.'),
            ],
          ),
        ),
      );
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.workspace_premium_outlined),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    current.plan.name,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                Chip(label: Text(_status(current.status))),
              ],
            ),
            const SizedBox(height: 8),
            if (current.periodEndsAt != null)
              Text('پایان دوره: ${_date(current.periodEndsAt!)}'),
            if (current.graceEndsAt != null)
              Text(
                'پایان مهلت تمدید: ${_date(current.graceEndsAt!)}',
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            if (current.cancelAtPeriodEnd)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text('لغو اشتراک برای پایان دوره ثبت شده است.'),
              ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (current.isInGrace)
                  FilledButton.icon(
                    onPressed: state.saving ? null : _renew,
                    icon: const Icon(Icons.autorenew),
                    label: const Text('تمدید اشتراک'),
                  ),
                if (!current.cancelAtPeriodEnd)
                  OutlinedButton(
                    onPressed: state.saving ? null : () => _cancel(context),
                    child: const Text('لغو در پایان دوره'),
                  )
                else
                  OutlinedButton(
                    onPressed:
                        state.saving
                            ? null
                            : () =>
                                ref
                                    .read(
                                      subscriptionControllerProvider.notifier,
                                    )
                                    .resume(),
                    child: const Text('ادامه اشتراک'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _usage(BuildContext context, List<SubscriptionUsage> usage) {
    if (usage.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('مصرف سهمیه‌ای برای این دوره ثبت نشده است.'),
        ),
      );
    }
    return Column(
      children:
          usage.map((row) {
            final total = row.limit;
            final consumed = row.used + row.reserved;
            final progress =
                row.unlimited || total == null || total <= 0
                    ? null
                    : (consumed / total).clamp(0.0, 1.0);
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(row.code),
                    const SizedBox(height: 8),
                    if (progress != null)
                      LinearProgressIndicator(value: progress),
                    const SizedBox(height: 6),
                    Text(
                      row.unlimited
                          ? 'مصرف‌شده ${_compact(row.used)} • نامحدود'
                          : 'مصرف‌شده ${_compact(row.used)} • رزروشده ${_compact(row.reserved)} • باقی‌مانده ${_compact(row.remaining ?? 0)}',
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
    );
  }

  Widget _planCard(
    BuildContext context,
    SubscriptionState state,
    SubscriptionPlan plan,
  ) {
    final active = state.current?.plan.code == plan.code;
    final features = plan.features.where((row) => row.enabled).take(5);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    plan.name,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                Text(
                  plan.isFree
                      ? 'رایگان'
                      : formatToman(context, plan.priceToman),
                ),
              ],
            ),
            if (plan.description != null) ...[
              const SizedBox(height: 6),
              Text(plan.description!),
            ],
            const SizedBox(height: 10),
            ...features.map(
              (feature) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_outline, size: 18),
                    const SizedBox(width: 6),
                    Expanded(child: Text(_featureLabel(feature))),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child:
                  active
                      ? const Chip(label: Text('پلن فعلی'))
                      : FilledButton(
                        onPressed:
                            state.saving
                                ? null
                                : () =>
                                    plan.isFree
                                        ? ref
                                            .read(
                                              subscriptionControllerProvider
                                                  .notifier,
                                            )
                                            .activateFree()
                                        : () => _checkout(plan),
                        child: Text(
                          plan.isFree ? 'فعال‌سازی رایگان' : 'خرید پلن',
                        ),
                      ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _checkout(SubscriptionPlan plan) async {
    final checkout = await ref
        .read(subscriptionControllerProvider.notifier)
        .checkout(plan, _provider);
    if (!mounted || checkout == null) return;
    await _handleCheckout(checkout);
  }

  Future<void> _renew() async {
    final checkout = await ref
        .read(subscriptionControllerProvider.notifier)
        .renewalCheckout(_provider);
    if (!mounted || checkout == null) return;
    await _handleCheckout(checkout);
  }

  Future<void> _handleCheckout(SubscriptionCheckout checkout) async {
    if (_provider == 'mock') {
      final ok = await ref
          .read(subscriptionControllerProvider.notifier)
          .verify(checkout, 'mobile-approved');
      if (mounted && ok) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('پرداخت آزمایشی تأیید و اشتراک فعال شد.'),
          ),
        );
      }
      return;
    }
    final link = checkout.redirectUrl;
    if (link == null || link.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: link));
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('ادامه پرداخت'),
            content: const Text(
              'لینک امن درگاه کپی شد. آن را در مرورگر باز کنید و پس از بازگشت، صفحه را تازه‌سازی کنید.',
            ),
            actions: [
              FilledButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('متوجه شدم'),
              ),
            ],
          ),
    );
  }

  Future<void> _cancel(BuildContext context) async {
    final controller = TextEditingController(
      text: 'درخواست کاربر برای پایان دوره',
    );
    final accepted = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('لغو اشتراک'),
            content: TextField(
              controller: controller,
              maxLength: 500,
              decoration: const InputDecoration(labelText: 'دلیل لغو'),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('ثبت لغو پایان دوره'),
              ),
            ],
          ),
    );
    if (accepted == true && mounted) {
      await ref
          .read(subscriptionControllerProvider.notifier)
          .cancel(controller.text.trim());
    }
  }

  Widget _errorCard(BuildContext context, String message) => Card(
    color: Theme.of(context).colorScheme.errorContainer,
    child: Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          Expanded(child: Text(message)),
          IconButton(
            onPressed:
                () => ref.read(subscriptionControllerProvider.notifier).load(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
    ),
  );

  String get _provider {
    final host = Uri.tryParse(AppConfig.apiBaseUrl)?.host;
    return host == 'localhost' || host == '127.0.0.1' ? 'mock' : 'zarinpal';
  }

  String _featureLabel(SubscriptionPlanFeature feature) {
    if (feature.unlimited) return '${feature.name}: نامحدود';
    if (feature.value == null || feature.value == true) return feature.name;
    return '${feature.name}: ${feature.value}${feature.unit == null ? '' : ' ${feature.unit}'}';
  }

  String _status(String value) => switch (value) {
    'active' => 'فعال',
    'grace' => 'مهلت تمدید',
    'cancelled' => 'لغوشده',
    'expired' => 'منقضی',
    _ => value,
  };

  String _date(DateTime value) =>
      '${value.year}/${value.month.toString().padLeft(2, '0')}/${value.day.toString().padLeft(2, '0')}';

  String _compact(double value) =>
      value == value.roundToDouble()
          ? value.toInt().toString()
          : value.toStringAsFixed(2);
}
