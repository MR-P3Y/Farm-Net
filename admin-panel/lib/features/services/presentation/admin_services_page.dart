import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_service_models.dart';
import '../state/admin_service_controller.dart';

class AdminServicesPage extends ConsumerStatefulWidget {
  const AdminServicesPage({super.key});
  @override
  ConsumerState<AdminServicesPage> createState() => _State();
}

class _State extends ConsumerState<AdminServicesPage> {
  bool loaded = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!loaded) {
      loaded = true;
      Future.microtask(
        () => ref.read(adminServiceControllerProvider.notifier).load(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(adminServiceControllerProvider);
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'مدیریت خدمات کشاورزی',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                onPressed:
                    s.saving
                        ? null
                        : () =>
                            ref
                                .read(adminServiceControllerProvider.notifier)
                                .load(),
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          if (s.error != null)
            Text(
              s.error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          const SizedBox(height: 12),
          Expanded(
            child:
                s.loading
                    ? const AdminLoadingView()
                    : DefaultTabController(
                      length: 4,
                      child: Column(
                        children: [
                          const TabBar(
                            tabs: [
                              Tab(text: 'دسته‌بندی‌ها'),
                              Tab(text: 'خدمات‌دهندگان'),
                              Tab(text: 'پیشنهادها'),
                              Tab(text: 'درخواست‌ها'),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Expanded(
                            child: TabBarView(
                              children: [
                                _Categories(s),
                                _Providers(s),
                                _Offers(s),
                                _Requests(s),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
          ),
        ],
      ),
    );
  }
}

class _Categories extends ConsumerWidget {
  const _Categories(this.s);
  final AdminServiceState s;
  @override
  Widget build(c, r) => Column(
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: FilledButton.icon(
          onPressed: s.saving ? null : () => _categoryDialog(c, r, null),
          icon: const Icon(Icons.add),
          label: const Text('دسته‌بندی جدید'),
        ),
      ),
      const SizedBox(height: 8),
      Expanded(
        child:
            s.categories.isEmpty
                ? const AdminEmptyView(message: 'دسته‌بندی‌ای وجود ندارد.')
                : ListView(
                  children:
                      s.categories
                          .map(
                            (x) => Card(
                              child: ListTile(
                                title: Text(x.title),
                                subtitle: Text(
                                  '${x.code} • ترتیب ${x.sortOrder}',
                                ),
                                leading: Icon(
                                  x.isActive
                                      ? Icons.check_circle
                                      : Icons.pause_circle,
                                ),
                                trailing: IconButton(
                                  icon: const Icon(Icons.edit),
                                  onPressed: () => _categoryDialog(c, r, x),
                                ),
                              ),
                            ),
                          )
                          .toList(),
                ),
      ),
    ],
  );
}

class _Providers extends ConsumerWidget {
  const _Providers(this.s);
  final AdminServiceState s;
  @override
  Widget build(c, r) => _paged(
    c,
    r,
    'provider',
    s.providerPage,
    s.providerTotal,
    s.providers
        .map(
          (x) => Card(
            child: ListTile(
              title: Text(x.displayName),
              subtitle: Text(
                '#${x.userId} • ${x.title ?? '-'} • ${x.cityName ?? '-'}',
              ),
              leading: _Status(x.status),
              trailing: _Actions(
                kind: 'provider',
                id: x.id,
                statuses: const ['approved', 'rejected', 'suspended'],
              ),
            ),
          ),
        )
        .toList(),
  );
}

class _Offers extends ConsumerWidget {
  const _Offers(this.s);
  final AdminServiceState s;
  @override
  Widget build(c, r) => _paged(
    c,
    r,
    'offer',
    s.offerPage,
    s.offerTotal,
    s.offers
        .map(
          (x) => Card(
            child: ListTile(
              title: Text(x.title),
              subtitle: Text(
                '${x.providerName ?? '#${x.providerProfileId}'} • ${x.categoryTitle ?? '-'} • ${x.pricingType}',
              ),
              leading: _Status(x.status),
              trailing: _Actions(
                kind: 'offer',
                id: x.id,
                statuses: const [
                  'approved',
                  'rejected',
                  'suspended',
                  'archived',
                ],
              ),
            ),
          ),
        )
        .toList(),
  );
}

class _Requests extends ConsumerWidget {
  const _Requests(this.s);
  final AdminServiceState s;
  @override
  Widget build(c, r) => _paged(
    c,
    r,
    'request',
    s.requestPage,
    s.requestTotal,
    s.requests
        .map(
          (x) => Card(
            child: ListTile(
              onTap: () async {
                final d = await r
                    .read(adminServiceControllerProvider.notifier)
                    .detail(x.id);
                if (d != null && c.mounted) _detailDialog(c, r, d);
              },
              title: Text(x.title ?? 'درخواست #${x.id}'),
              subtitle: Text(
                'درخواست‌دهنده #${x.requesterUserId} • ${x.cityName ?? '-'}',
              ),
              leading: _Status(x.status),
              trailing: _Actions(
                kind: 'request',
                id: x.id,
                statuses: _transitions[x.status] ?? const [],
              ),
            ),
          ),
        )
        .toList(),
  );
}

const _transitions = {
  'open': ['accepted', 'rejected', 'cancelled'],
  'accepted': ['in_progress', 'cancelled'],
  'in_progress': ['completed', 'cancelled'],
};
Widget _paged(
  BuildContext c,
  WidgetRef r,
  String kind,
  int page,
  int total,
  List<Widget> rows,
) => Column(
  children: [
    Expanded(
      child:
          rows.isEmpty
              ? const AdminEmptyView(message: 'موردی برای نمایش وجود ندارد.')
              : ListView(children: rows),
    ),
    Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed:
              page > 1
                  ? () => r
                      .read(adminServiceControllerProvider.notifier)
                      .page(kind, page - 1)
                  : null,
          icon: const Icon(Icons.chevron_right),
        ),
        Text('صفحه $page • $total مورد'),
        IconButton(
          onPressed:
              page * 20 < total
                  ? () => r
                      .read(adminServiceControllerProvider.notifier)
                      .page(kind, page + 1)
                  : null,
          icon: const Icon(Icons.chevron_left),
        ),
      ],
    ),
  ],
);

class _Status extends StatelessWidget {
  const _Status(this.value);
  final String value;
  @override
  Widget build(c) => Chip(label: Text(value));
}

class _Actions extends ConsumerWidget {
  const _Actions({
    required this.kind,
    required this.id,
    required this.statuses,
  });
  final String kind;
  final int id;
  final List<String> statuses;
  @override
  Widget build(c, r) => PopupMenuButton<String>(
    enabled: statuses.isNotEmpty,
    itemBuilder:
        (_) =>
            statuses
                .map((x) => PopupMenuItem(value: x, child: Text(x)))
                .toList(),
    onSelected: (x) => _moderate(c, r, kind, id, x),
  );
}

Future<void> _moderate(
  BuildContext c,
  WidgetRef r,
  String kind,
  int id,
  String status,
) async {
  final note = TextEditingController();
  final ok = await showDialog<bool>(
    context: c,
    builder:
        (d) => AlertDialog(
          title: Text('تغییر وضعیت به $status'),
          content: TextField(
            controller: note,
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'یادداشت ادمین'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(d, false),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(d, true),
              child: const Text('ثبت'),
            ),
          ],
        ),
  );
  if (ok == true) {
    await r
        .read(adminServiceControllerProvider.notifier)
        .moderate(
          kind,
          id,
          status,
          note.text.trim().isEmpty ? null : note.text.trim(),
        );
  }
  note.dispose();
}

Future<void> _categoryDialog(
  BuildContext c,
  WidgetRef r,
  AdminServiceCategory? x,
) async {
  final code = TextEditingController(text: x?.code),
      title = TextEditingController(text: x?.title),
      desc = TextEditingController(text: x?.description),
      sort = TextEditingController(text: '${x?.sortOrder ?? 100}');
  bool active = x?.isActive ?? true;
  await showDialog<void>(
    context: c,
    builder:
        (d) => StatefulBuilder(
          builder:
              (d, set) => AlertDialog(
                title: Text(x == null ? 'دسته‌بندی جدید' : 'ویرایش دسته‌بندی'),
                content: SizedBox(
                  width: 480,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextField(
                        controller: code,
                        decoration: const InputDecoration(labelText: 'کد'),
                      ),
                      TextField(
                        controller: title,
                        decoration: const InputDecoration(labelText: 'عنوان'),
                      ),
                      TextField(
                        controller: desc,
                        decoration: const InputDecoration(labelText: 'توضیحات'),
                      ),
                      TextField(
                        controller: sort,
                        decoration: const InputDecoration(labelText: 'ترتیب'),
                        keyboardType: TextInputType.number,
                      ),
                      SwitchListTile(
                        value: active,
                        onChanged: (v) => set(() => active = v),
                        title: const Text('فعال'),
                      ),
                    ],
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(d),
                    child: const Text('انصراف'),
                  ),
                  FilledButton(
                    onPressed: () async {
                      if (code.text.trim().length < 2 ||
                          title.text.trim().length < 2) {
                        return;
                      }
                      final ok = await r
                          .read(adminServiceControllerProvider.notifier)
                          .saveCategory(x?.id, {
                            'code': code.text.trim(),
                            'title': title.text.trim(),
                            'description':
                                desc.text.trim().isEmpty
                                    ? null
                                    : desc.text.trim(),
                            'sort_order': int.tryParse(sort.text) ?? 100,
                            'is_active': active,
                          });
                      if (ok && d.mounted) Navigator.pop(d);
                    },
                    child: const Text('ذخیره'),
                  ),
                ],
              ),
        ),
  );
  code.dispose();
  title.dispose();
  desc.dispose();
  sort.dispose();
}

Future<void> _detailDialog(
  BuildContext c,
  WidgetRef r,
  AdminServiceRequest x,
) => showDialog<void>(
  context: c,
  builder:
      (d) => AlertDialog(
        title: Text('درخواست #${x.id}'),
        content: SizedBox(
          width: 650,
          child: ListView(
            shrinkWrap: true,
            children: [
              Text(x.description ?? 'بدون توضیحات'),
              const Divider(),
              Text('تاریخچه وضعیت', style: Theme.of(c).textTheme.titleMedium),
              ...x.statusLogs.map(
                (l) => ListTile(
                  dense: true,
                  title: Text('${l.oldStatus ?? '-'} ← ${l.newStatus}'),
                  subtitle: Text(
                    '${l.createdAt}${l.note == null ? '' : ' • ${l.note}'}',
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(d),
            child: const Text('بستن'),
          ),
        ],
      ),
);
