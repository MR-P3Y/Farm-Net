import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_price_text.dart';
import '../../../core/widgets/farm_search_field.dart';
import '../data/search_models.dart';
import '../state/search_controller.dart';

class UnifiedSearchScreen extends ConsumerStatefulWidget {
  const UnifiedSearchScreen({super.key});

  @override
  ConsumerState<UnifiedSearchScreen> createState() =>
      _UnifiedSearchScreenState();
}

class _UnifiedSearchScreenState extends ConsumerState<UnifiedSearchScreen> {
  final _queryController = TextEditingController();

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(searchControllerProvider);
    return Scaffold(
      appBar: const FarmAppBar(title: 'جستجوی همه بخش‌ها'),
      body: ResponsiveBuilder(
        builder:
            (context, constraints, r) => Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: ListView(
                  padding: r.pagePadding(),
                  children: [
                    FarmSearchField(
                      controller: _queryController,
                      hint: 'محصول، خدمت، تجهیزات، مشاور یا مطلب...',
                      onChanged: (value) {
                        if (value.length > 2) _search();
                      },
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'جستجو در',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children:
                          searchResultTypes
                              .map(
                                (type) => FilterChip(
                                  label: Text(searchTypeLabels[type] ?? type),
                                  selected: state.types.contains(type),
                                  onSelected:
                                      (_) => ref
                                          .read(
                                            searchControllerProvider.notifier,
                                          )
                                          .toggleType(type),
                                ),
                              )
                              .toList(),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: state.sort,
                      decoration: const InputDecoration(labelText: 'مرتب‌سازی'),
                      items: const [
                        DropdownMenuItem(
                          value: 'relevance',
                          child: Text('مرتبط‌ترین'),
                        ),
                        DropdownMenuItem(
                          value: 'newest',
                          child: Text('جدیدترین'),
                        ),
                        DropdownMenuItem(
                          value: 'price_asc',
                          child: Text('کمترین قیمت'),
                        ),
                        DropdownMenuItem(
                          value: 'price_desc',
                          child: Text('بیشترین قیمت'),
                        ),
                        DropdownMenuItem(
                          value: 'rating',
                          child: Text('بالاترین امتیاز'),
                        ),
                      ],
                      onChanged:
                          state.isLoading
                              ? null
                              : (value) {
                                if (value != null) {
                                  ref
                                      .read(searchControllerProvider.notifier)
                                      .setSort(value);
                                }
                              },
                    ),
                    const SizedBox(height: 20),
                    if (state.isLoading)
                      const Center(child: CircularProgressIndicator())
                    else if (state.errorMessage != null)
                      _ErrorState(
                        message: state.errorMessage!,
                        onRetry: state.query.isEmpty ? null : _search,
                      )
                    else if (!state.hasSearched)
                      const _InitialState()
                    else if (state.result == null || state.result!.total == 0)
                      const _EmptyState()
                    else
                      ...state.result!.groups
                          .where((group) => group.items.isNotEmpty)
                          .map((group) => _ResultGroup(group: group)),
                  ],
                ),
              ),
            ),
      ),
    );
  }

  void _search() =>
      ref.read(searchControllerProvider.notifier).search(_queryController.text);
}

class _ResultGroup extends StatelessWidget {
  const _ResultGroup({required this.group});
  final SearchResultGroup group;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Padding(
        padding: const EdgeInsets.only(top: 8, bottom: 6),
        child: Text(
          '${searchTypeLabels[group.type] ?? group.type} (${group.total})',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      ...group.items.map(
        (item) => Card(
          child: ListTile(
            leading: CircleAvatar(child: Icon(_iconFor(item.type))),
            title: Text(item.title),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (item.subtitle?.trim().isNotEmpty == true)
                  Text(
                    item.subtitle!,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                if (item.price != null && item.currency == 'TOMAN')
                  FarmPriceText(amountToman: item.price!),
                if (item.rating != null) Text('امتیاز ${item.rating}'),
              ],
            ),
            trailing: const Icon(Icons.chevron_left),
            onTap:
                item.route.startsWith('/')
                    ? () => context.push(item.route)
                    : null,
          ),
        ),
      ),
      const SizedBox(height: 12),
    ],
  );

  IconData _iconFor(String type) => switch (type) {
    'product' => Icons.inventory_2_outlined,
    'store' => Icons.storefront_outlined,
    'service' => Icons.home_repair_service_outlined,
    'rental_equipment' => Icons.agriculture_outlined,
    'consultant' => Icons.support_agent_outlined,
    _ => Icons.groups_2_outlined,
  };
}

class _InitialState extends StatelessWidget {
  const _InitialState();
  @override
  Widget build(BuildContext context) => const Padding(
    padding: EdgeInsets.all(32),
    child: Column(
      children: [
        Icon(Icons.manage_search, size: 64),
        SizedBox(height: 12),
        Text('یک عبارت بنویسید تا همه بخش‌های فارم‌نت جستجو شوند.'),
      ],
    ),
  );
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();
  @override
  Widget build(BuildContext context) => const Padding(
    padding: EdgeInsets.all(32),
    child: Column(
      children: [
        Icon(Icons.search_off, size: 64),
        SizedBox(height: 12),
        Text('نتیجه‌ای پیدا نشد. عبارت یا بخش‌های انتخابی را تغییر دهید.'),
      ],
    ),
  );
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback? onRetry;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Column(
      children: [
        const Icon(Icons.error_outline, size: 56),
        const SizedBox(height: 8),
        Text(message, textAlign: TextAlign.center),
        if (onRetry != null)
          TextButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('تلاش دوباره'),
          ),
      ],
    ),
  );
}
