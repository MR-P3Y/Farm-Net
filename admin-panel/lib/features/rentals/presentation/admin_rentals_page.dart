import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_rental_models.dart';
import '../state/admin_rental_controller.dart';

class AdminRentalsPage extends ConsumerStatefulWidget {
  const AdminRentalsPage({super.key});
  @override
  ConsumerState<AdminRentalsPage> createState() => _State();
}

class _State extends ConsumerState<AdminRentalsPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(adminRentalControllerProvider.notifier).load(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(adminRentalControllerProvider);
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'مدیریت اجاره تجهیزات',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                onPressed:
                    s.saving
                        ? null
                        : () =>
                            ref
                                .read(adminRentalControllerProvider.notifier)
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
                              Tab(text: 'دسته‌ها'),
                              Tab(text: 'موجران'),
                              Tab(text: 'تجهیزات'),
                              Tab(text: 'درخواست‌ها'),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Expanded(
                            child: TabBarView(
                              children: [
                                _Categories(s),
                                _Profiles(s),
                                _Equipment(s),
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
  final AdminRentalState s;
  @override
  Widget build(c, r) => Column(
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: FilledButton.icon(
          onPressed: s.saving ? null : () => _category(c, r, null),
          icon: const Icon(Icons.add),
          label: const Text('دسته جدید'),
        ),
      ),
      Expanded(
        child:
            s.categories.isEmpty
                ? const AdminEmptyView(message: 'دسته‌ای وجود ندارد.')
                : ListView(
                  children:
                      s.categories
                          .map(
                            (x) => Card(
                              child: ListTile(
                                title: Text(x.title),
                                subtitle: Text(
                                  '${x.code} • ${x.equipmentCount} تجهیز • ${x.childrenCount} فرزند',
                                ),
                                leading: Icon(
                                  x.isActive
                                      ? Icons.check_circle
                                      : Icons.pause_circle,
                                ),
                                trailing: IconButton(
                                  onPressed: () => _category(c, r, x),
                                  icon: const Icon(Icons.edit),
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

class _Profiles extends ConsumerWidget {
  const _Profiles(this.s);
  final AdminRentalState s;
  @override
  Widget build(c, r) => _paged(
    r,
    'profile',
    s.profilePage,
    s.profileTotal,
    s.profiles
        .map(
          (x) => Card(
            child: ListTile(
              title: Text(x.displayName ?? 'موجر #${x.id}'),
              subtitle: Text(
                'کاربر #${x.userId} • ${x.equipmentCount} تجهیز • ${x.phone ?? '-'}',
              ),
              leading: _Status(x.status),
              trailing: _Actions(
                kind: 'profile',
                id: x.id,
                statuses: const [
                  'approved',
                  'rejected',
                  'suspended',
                  'pending_review',
                ],
              ),
            ),
          ),
        )
        .toList(),
  );
}

class _Equipment extends ConsumerWidget {
  const _Equipment(this.s);
  final AdminRentalState s;
  @override
  Widget build(c, r) => _paged(
    r,
    'equipment',
    s.equipmentPage,
    s.equipmentTotal,
    s.equipment
        .map(
          (x) => Card(
            child: ListTile(
              title: Text(x.title),
              subtitle: Text(
                'موجر #${x.lessorProfileId} • ${x.mediaCount} رسانه • ${x.operatorMode}',
              ),
              leading: _Status(x.status),
              trailing: _Actions(
                kind: 'equipment',
                id: x.id,
                statuses: const [
                  'approved',
                  'rejected',
                  'suspended',
                  'pending_review',
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
  final AdminRentalState s;
  @override
  Widget build(c, r) => _paged(
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
                    .read(adminRentalControllerProvider.notifier)
                    .detail(x.id);
                if (d != null && c.mounted) _detail(c, d);
              },
              title: Text(x.equipmentTitle),
              subtitle: Text(
                'متقاضی #${x.requesterUserId} • موجر #${x.lessorProfileId}',
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
  'pending': ['accepted', 'rejected', 'cancelled'],
  'accepted': ['in_progress', 'cancelled'],
  'in_progress': ['completed', 'cancelled'],
};
Widget _paged(
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
              ? const AdminEmptyView(message: 'موردی وجود ندارد.')
              : ListView(children: rows),
    ),
    Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed:
              page > 1
                  ? () => r
                      .read(adminRentalControllerProvider.notifier)
                      .page(kind, page - 1)
                  : null,
          icon: const Icon(Icons.chevron_right),
        ),
        Text('صفحه $page • $total مورد'),
        IconButton(
          onPressed:
              page * 20 < total
                  ? () => r
                      .read(adminRentalControllerProvider.notifier)
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
            decoration: InputDecoration(
              labelText:
                  (status == 'rejected' || status == 'suspended')
                      ? 'یادداشت ادمین — الزامی'
                      : 'یادداشت ادمین',
            ),
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
    if ((status == 'rejected' || status == 'suspended') &&
        note.text.trim().isEmpty) {
      note.dispose();
      return;
    }
    await r
        .read(adminRentalControllerProvider.notifier)
        .moderate(
          kind,
          id,
          status,
          note.text.trim().isEmpty ? null : note.text.trim(),
        );
  }
  note.dispose();
}

Future<void> _category(
  BuildContext c,
  WidgetRef r,
  AdminRentalCategory? x,
) async {
  final code = TextEditingController(text: x?.code),
      title = TextEditingController(text: x?.title),
      description = TextEditingController(text: x?.description),
      sort = TextEditingController(text: '${x?.sortOrder ?? 100}');
  bool active = x?.isActive ?? true;
  int? parentId = x?.parentId;
  final categories = r.read(adminRentalControllerProvider).categories;
  await showDialog<void>(
    context: c,
    builder:
        (d) => StatefulBuilder(
          builder:
              (d, set) => AlertDialog(
                title: Text(x == null ? 'دسته جدید' : 'ویرایش دسته'),
                content: Column(
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
                    DropdownButtonFormField<int?>(
                      initialValue: parentId,
                      decoration: const InputDecoration(labelText: 'دسته والد'),
                      items: [
                        const DropdownMenuItem<int?>(
                          value: null,
                          child: Text('بدون والد'),
                        ),
                        ...categories
                            .where((item) => item.id != x?.id)
                            .map(
                              (item) => DropdownMenuItem<int?>(
                                value: item.id,
                                child: Text(item.title),
                              ),
                            ),
                      ],
                      onChanged: (value) => set(() => parentId = value),
                    ),
                    TextField(
                      controller: description,
                      decoration: const InputDecoration(labelText: 'توضیحات'),
                    ),
                    TextField(
                      controller: sort,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'ترتیب'),
                    ),
                    SwitchListTile(
                      value: active,
                      onChanged: (v) => set(() => active = v),
                      title: const Text('فعال'),
                    ),
                  ],
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
                          .read(adminRentalControllerProvider.notifier)
                          .saveCategory(x?.id, {
                            'code': code.text.trim(),
                            'title': title.text.trim(),
                            'parent_id': parentId,
                            'description':
                                description.text.trim().isEmpty
                                    ? null
                                    : description.text.trim(),
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
  description.dispose();
  sort.dispose();
}

Future<void> _detail(BuildContext c, AdminRentalRequest x) => showDialog<void>(
  context: c,
  builder:
      (d) => AlertDialog(
        title: Text('درخواست #${x.id}'),
        content: SizedBox(
          width: 650,
          child: ListView(
            shrinkWrap: true,
            children: [
              Text(
                '${x.equipmentTitle} • ${x.totalAmount?.toStringAsFixed(0) ?? '-'} ${x.currency == 'TOMAN' ? 'تومان' : x.currency}',
              ),
              if ((x.adminNote ?? '').isNotEmpty)
                Text('یادداشت ادمین: ${x.adminNote}'),
              if ((x.cancelReason ?? '').isNotEmpty)
                Text('دلیل لغو: ${x.cancelReason}'),
              const Divider(),
              ...x.statusLogs.map(
                (l) => ListTile(
                  title: Text('${l.fromStatus ?? '-'} ← ${l.toStatus}'),
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
