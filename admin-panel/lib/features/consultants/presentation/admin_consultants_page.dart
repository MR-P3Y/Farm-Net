import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/admin_responsive.dart';
import '../../../core/widgets/admin_data_table.dart';
import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_consultant_models.dart';
import '../state/admin_consultant_controller.dart';
import '../state/admin_consultant_state.dart';

class AdminConsultantsPage extends ConsumerStatefulWidget {
  const AdminConsultantsPage({super.key, this.initialTab = 0});

  final int initialTab;

  @override
  ConsumerState<AdminConsultantsPage> createState() =>
      _AdminConsultantsPageState();
}

class _AdminConsultantsPageState extends ConsumerState<AdminConsultantsPage> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(adminConsultantControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(adminConsultantControllerProvider);

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
                    'مدیریت مشاوران',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'بروزرسانی',
                    onPressed:
                        state.isSaving
                            ? null
                            : () =>
                                ref
                                    .read(
                                      adminConsultantControllerProvider
                                          .notifier,
                                    )
                                    .load(),
                    icon: const Icon(Icons.refresh),
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
                        : DefaultTabController(
                          length: 3,
                          initialIndex: widget.initialTab,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              _SummaryRow(state: state),
                              const SizedBox(height: 12),
                              const TabBar(
                                tabs: [
                                  Tab(
                                    icon: Icon(Icons.badge_outlined),
                                    text: 'پروفایل‌ها',
                                  ),
                                  Tab(
                                    icon: Icon(Icons.category_outlined),
                                    text: 'تخصص‌ها',
                                  ),
                                  Tab(
                                    icon: Icon(Icons.support_agent_outlined),
                                    text: 'درخواست‌ها',
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Expanded(
                                child: TabBarView(
                                  children: [
                                    _ProfilesTab(
                                      profiles: state.profiles,
                                      selectedStatus: state.profileStatusFilter,
                                      isSaving: state.isSaving,
                                    ),
                                    _SpecialtiesTab(
                                      specialties: state.specialties,
                                      isSaving: state.isSaving,
                                    ),
                                    _RequestsTab(
                                      requests: state.requests,
                                      selectedStatus: state.requestStatusFilter,
                                      isSaving: state.isSaving,
                                    ),
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
      },
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({required this.state});

  final AdminConsultantState state;

  @override
  Widget build(BuildContext context) {
    final pending =
        state.profiles.where((item) => item.status == 'pending_review').length;
    final approved =
        state.profiles.where((item) => item.status == 'approved').length;
    final openRequests =
        state.requests.where((item) => item.status == 'open').length;

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        _SummaryCard(
          icon: Icons.badge_outlined,
          label: 'کل مشاوران',
          value: state.profiles.length.toString(),
        ),
        _SummaryCard(
          icon: Icons.pending_actions_outlined,
          label: 'در انتظار بررسی',
          value: pending.toString(),
        ),
        _SummaryCard(
          icon: Icons.verified_outlined,
          label: 'تأیید شده',
          value: approved.toString(),
        ),
        _SummaryCard(
          icon: Icons.mark_unread_chat_alt_outlined,
          label: 'درخواست باز',
          value: openRequests.toString(),
        ),
      ],
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(icon),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(label),
                    const SizedBox(height: 4),
                    Text(value, style: Theme.of(context).textTheme.titleLarge),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProfilesTab extends ConsumerWidget {
  const _ProfilesTab({
    required this.profiles,
    required this.selectedStatus,
    required this.isSaving,
  });

  final List<AdminConsultProfile> profiles;
  final String? selectedStatus;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        _FilterBar(
          label: 'وضعیت پروفایل',
          value: selectedStatus,
          statuses: const [
            'pending_review',
            'approved',
            'rejected',
            'suspended',
            'draft',
          ],
          onChanged:
              isSaving
                  ? null
                  : (status) => ref
                      .read(adminConsultantControllerProvider.notifier)
                      .filterProfiles(status),
        ),
        const SizedBox(height: 12),
        if (profiles.isEmpty)
          const AdminEmptyView(message: 'پروفایل مشاوری برای نمایش وجود ندارد.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('کاربر')),
              DataColumn(label: Text('نام')),
              DataColumn(label: Text('عنوان')),
              DataColumn(label: Text('تخصص‌ها')),
              DataColumn(label: Text('وضعیت')),
              DataColumn(label: Text('امتیاز')),
              DataColumn(label: Text('عملیات')),
            ],
            rows:
                profiles.map((profile) {
                  return DataRow(
                    cells: [
                      DataCell(Text(profile.id.toString())),
                      DataCell(Text('#${profile.userId}')),
                      DataCell(Text(profile.displayName ?? '-')),
                      DataCell(Text(profile.title ?? '-')),
                      DataCell(Text(profile.specialtyText)),
                      DataCell(_StatusChip(status: profile.status)),
                      DataCell(
                        Text(
                          '${profile.ratingAverage} (${profile.reviewsCount})',
                        ),
                      ),
                      DataCell(
                        Wrap(
                          spacing: 6,
                          children: [
                            IconButton(
                              tooltip: 'تأیید',
                              onPressed:
                                  isSaving
                                      ? null
                                      : () => _openProfileStatusDialog(
                                        context,
                                        ref,
                                        profile,
                                        'approved',
                                      ),
                              icon: const Icon(Icons.check_circle_outline),
                            ),
                            IconButton(
                              tooltip: 'رد',
                              onPressed:
                                  isSaving
                                      ? null
                                      : () => _openProfileStatusDialog(
                                        context,
                                        ref,
                                        profile,
                                        'rejected',
                                      ),
                              icon: const Icon(Icons.cancel_outlined),
                            ),
                            IconButton(
                              tooltip: 'تعلیق',
                              onPressed:
                                  isSaving
                                      ? null
                                      : () => _openProfileStatusDialog(
                                        context,
                                        ref,
                                        profile,
                                        'suspended',
                                      ),
                              icon: const Icon(Icons.block_outlined),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }

  Future<void> _openProfileStatusDialog(
    BuildContext context,
    WidgetRef ref,
    AdminConsultProfile profile,
    String status,
  ) async {
    final noteController = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: Text('${_statusLabel(status)} مشاور #${profile.id}'),
          content: SizedBox(
            width: 520,
            child: TextField(
              controller: noteController,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'یادداشت ادمین',
                border: OutlineInputBorder(),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('انصراف'),
            ),
            FilledButton.icon(
              onPressed: () async {
                final ok = await ref
                    .read(adminConsultantControllerProvider.notifier)
                    .updateProfileStatus(
                      id: profile.id,
                      status: status,
                      note:
                          noteController.text.trim().isEmpty
                              ? null
                              : noteController.text.trim(),
                    );

                if (ok && context.mounted) Navigator.pop(context);
              },
              icon: const Icon(Icons.save_outlined),
              label: const Text('ثبت'),
            ),
          ],
        );
      },
    );

    noteController.dispose();
  }
}

class _SpecialtiesTab extends ConsumerWidget {
  const _SpecialtiesTab({required this.specialties, required this.isSaving});

  final List<AdminConsultSpecialty> specialties;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        Row(
          children: [
            Text(
              'تخصص‌های مشاوره',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed:
                  isSaving
                      ? null
                      : () => _openSpecialtyDialog(context, ref, null),
              icon: const Icon(Icons.add),
              label: const Text('افزودن تخصص'),
            ),
          ],
        ),
        const SizedBox(height: 12),
        TextFormField(
          decoration: const InputDecoration(
            labelText: 'جستجوی کد، عنوان یا توضیحات تخصص',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.search),
          ),
          textInputAction: TextInputAction.search,
          onFieldSubmitted:
              (value) => ref
                  .read(adminConsultantControllerProvider.notifier)
                  .searchSpecialties(value),
        ),
        const SizedBox(height: 12),
        if (specialties.isEmpty)
          const AdminEmptyView(message: 'تخصصی ثبت نشده است.')
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('کد')),
              DataColumn(label: Text('عنوان')),
              DataColumn(label: Text('ترتیب')),
              DataColumn(label: Text('فعال')),
              DataColumn(label: Text('پروفایل‌ها')),
              DataColumn(label: Text('درخواست‌ها')),
              DataColumn(label: Text('عملیات')),
            ],
            rows:
                specialties.map((specialty) {
                  return DataRow(
                    cells: [
                      DataCell(Text(specialty.id.toString())),
                      DataCell(Text(specialty.code)),
                      DataCell(Text(specialty.title)),
                      DataCell(Text(specialty.sortOrder.toString())),
                      DataCell(Text(specialty.isActive ? 'بله' : 'خیر')),
                      DataCell(Text(specialty.profilesCount.toString())),
                      DataCell(Text(specialty.requestsCount.toString())),
                      DataCell(
                        TextButton.icon(
                          onPressed:
                              isSaving
                                  ? null
                                  : () => _openSpecialtyDialog(
                                    context,
                                    ref,
                                    specialty,
                                  ),
                          icon: const Icon(Icons.edit_outlined),
                          label: const Text('ویرایش'),
                        ),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }

  Future<void> _openSpecialtyDialog(
    BuildContext context,
    WidgetRef ref,
    AdminConsultSpecialty? specialty,
  ) async {
    final codeController = TextEditingController(text: specialty?.code ?? '');
    final titleController = TextEditingController(text: specialty?.title ?? '');
    final descriptionController = TextEditingController(
      text: specialty?.description ?? '',
    );
    final sortOrderController = TextEditingController(
      text: (specialty?.sortOrder ?? 100).toString(),
    );
    var isActive = specialty?.isActive ?? true;

    await showDialog<void>(
      context: context,
      builder: (_) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text(specialty == null ? 'افزودن تخصص' : 'ویرایش تخصص'),
              content: SizedBox(
                width: 560,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextField(
                        controller: codeController,
                        decoration: const InputDecoration(
                          labelText: 'کد انگلیسی',
                          hintText: 'pistachio_disease',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: titleController,
                        decoration: const InputDecoration(
                          labelText: 'عنوان',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: descriptionController,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          labelText: 'توضیح',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: sortOrderController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'ترتیب نمایش',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 8),
                      SwitchListTile(
                        value: isActive,
                        title: const Text('فعال باشد'),
                        onChanged: (value) => setState(() => isActive = value),
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
                FilledButton.icon(
                  onPressed: () async {
                    final sortOrder =
                        int.tryParse(sortOrderController.text.trim()) ?? 100;
                    final code = codeController.text.trim();
                    final title = titleController.text.trim();

                    if (code.isEmpty || title.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('کد و عنوان تخصص الزامی است.'),
                        ),
                      );
                      return;
                    }

                    final ok = await ref
                        .read(adminConsultantControllerProvider.notifier)
                        .saveSpecialty(
                          id: specialty?.id,
                          code: code,
                          title: title,
                          description:
                              descriptionController.text.trim().isEmpty
                                  ? null
                                  : descriptionController.text.trim(),
                          sortOrder: sortOrder,
                          isActive: isActive,
                        );

                    if (ok && context.mounted) Navigator.pop(context);
                  },
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('ذخیره'),
                ),
              ],
            );
          },
        );
      },
    );

    codeController.dispose();
    titleController.dispose();
    descriptionController.dispose();
    sortOrderController.dispose();
  }
}

class _RequestsTab extends ConsumerWidget {
  const _RequestsTab({
    required this.requests,
    required this.selectedStatus,
    required this.isSaving,
  });

  final List<AdminConsultRequest> requests;
  final String? selectedStatus;
  final bool isSaving;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      children: [
        _FilterBar(
          label: 'وضعیت درخواست',
          value: selectedStatus,
          statuses: const [
            'open',
            'accepted',
            'in_progress',
            'completed',
            'cancelled',
            'rejected',
          ],
          onChanged:
              isSaving
                  ? null
                  : (status) => ref
                      .read(adminConsultantControllerProvider.notifier)
                      .filterRequests(status),
        ),
        const SizedBox(height: 12),
        if (requests.isEmpty)
          const AdminEmptyView(
            message: 'درخواست مشاوره‌ای برای نمایش وجود ندارد.',
          )
        else
          AdminDataTable(
            columns: const [
              DataColumn(label: Text('ID')),
              DataColumn(label: Text('کاربر')),
              DataColumn(label: Text('مشاور')),
              DataColumn(label: Text('تخصص')),
              DataColumn(label: Text('عنوان')),
              DataColumn(label: Text('وضعیت')),
              DataColumn(label: Text('بودجه')),
              DataColumn(label: Text('عملیات')),
            ],
            rows:
                requests.map((request) {
                  return DataRow(
                    cells: [
                      DataCell(Text(request.id.toString())),
                      DataCell(Text('#${request.requesterUserId}')),
                      DataCell(Text(request.consultant?.displayName ?? '-')),
                      DataCell(Text(request.specialty?.title ?? '-')),
                      DataCell(Text(request.title)),
                      DataCell(_StatusChip(status: request.status)),
                      DataCell(
                        Text(
                          request.budgetAmount == null
                              ? '-'
                              : '${request.budgetAmount} ${request.currency}',
                        ),
                      ),
                      DataCell(
                        Wrap(
                          spacing: 6,
                          children: [
                            TextButton.icon(
                              onPressed:
                                  isSaving
                                      ? null
                                      : () => _openRequestDetailDialog(
                                        context,
                                        ref,
                                        request,
                                      ),
                              icon: const Icon(Icons.visibility_outlined),
                              label: const Text('جزئیات'),
                            ),
                            TextButton.icon(
                              onPressed:
                                  isSaving
                                      ? null
                                      : () => _openRequestStatusDialog(
                                        context,
                                        ref,
                                        request,
                                      ),
                              icon: const Icon(Icons.edit_note_outlined),
                              label: const Text('وضعیت'),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                }).toList(),
          ),
      ],
    );
  }

  Future<void> _openRequestDetailDialog(
    BuildContext context,
    WidgetRef ref,
    AdminConsultRequest request,
  ) async {
    final ok = await ref
        .read(adminConsultantControllerProvider.notifier)
        .loadRequestDetail(request.id);

    if (!ok || !context.mounted) return;

    await showDialog<void>(
      context: context,
      builder: (_) {
        return Consumer(
          builder: (dialogContext, ref, _) {
            final state = ref.watch(adminConsultantControllerProvider);
            final detail = state.selectedRequest ?? request;

            return AlertDialog(
              title: Text('جزئیات درخواست #${detail.id}'),
              content: SizedBox(
                width: 760,
                child: SingleChildScrollView(
                  child: _RequestDetailContent(request: detail),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('بستن'),
                ),
                FilledButton.icon(
                  onPressed:
                      state.isSaving
                          ? null
                          : () {
                            Navigator.pop(dialogContext);
                            _openRequestStatusDialog(context, ref, detail);
                          },
                  icon: const Icon(Icons.edit_note_outlined),
                  label: const Text('تغییر وضعیت'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _openRequestStatusDialog(
    BuildContext context,
    WidgetRef ref,
    AdminConsultRequest request,
  ) async {
    final noteController = TextEditingController();
    var status = request.status;

    await showDialog<void>(
      context: context,
      builder: (_) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text('تغییر وضعیت درخواست #${request.id}'),
              content: SizedBox(
                width: 520,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<String>(
                      initialValue: status,
                      decoration: const InputDecoration(
                        labelText: 'وضعیت',
                        border: OutlineInputBorder(),
                      ),
                      items:
                          const [
                                'open',
                                'accepted',
                                'in_progress',
                                'completed',
                                'cancelled',
                                'rejected',
                              ]
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(_statusLabel(item)),
                                ),
                              )
                              .toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => status = value);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: noteController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'یادداشت',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('انصراف'),
                ),
                FilledButton.icon(
                  onPressed: () async {
                    final ok = await ref
                        .read(adminConsultantControllerProvider.notifier)
                        .updateRequestStatus(
                          id: request.id,
                          status: status,
                          note:
                              noteController.text.trim().isEmpty
                                  ? null
                                  : noteController.text.trim(),
                        );

                    if (ok && context.mounted) Navigator.pop(context);
                  },
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('ثبت'),
                ),
              ],
            );
          },
        );
      },
    );

    noteController.dispose();
  }
}

class _RequestDetailContent extends StatelessWidget {
  const _RequestDetailContent({required this.request});

  final AdminConsultRequest request;

  @override
  Widget build(BuildContext context) {
    final consultantName = request.consultant?.displayName;
    final rows = [
      ('درخواست‌دهنده', '#${request.requesterUserId}'),
      if (consultantName != null && consultantName.trim().isNotEmpty)
        ('مشاور', '$consultantName (#${request.consultantProfileId ?? '-'})'),
      if (request.specialty?.title.trim().isNotEmpty == true)
        ('تخصص', request.specialty!.title),
      ('روش ارتباط', _contactMethodLabel(request.contactMethod)),
      ('وضعیت', _statusLabel(request.status)),
      ('ثبت', _compactDate(request.createdAt)),
      ('آخرین تغییر', _compactDate(request.updatedAt)),
      if (request.scheduledAt != null)
        ('زمان پیشنهادی', _compactDate(request.scheduledAt!)),
      if (request.budgetAmount != null)
        ('بودجه', '${request.budgetAmount} ${request.currency}'),
    ];

    final notes = [
      if (request.adminNote != null && request.adminNote!.trim().isNotEmpty)
        ('یادداشت ادمین', request.adminNote!),
      if (request.consultantNote != null &&
          request.consultantNote!.trim().isNotEmpty)
        ('یادداشت مشاور', request.consultantNote!),
      if (request.cancelReason != null &&
          request.cancelReason!.trim().isNotEmpty)
        ('دلیل لغو', request.cancelReason!),
      if (request.acceptedAt != null)
        ('پذیرش', _compactDate(request.acceptedAt!)),
      if (request.completedAt != null)
        ('تکمیل', _compactDate(request.completedAt!)),
      if (request.cancelledAt != null)
        ('لغو', _compactDate(request.cancelledAt!)),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _DetailSection(title: request.title, child: Text(request.description)),
        const SizedBox(height: 12),
        _DetailSection(
          title: 'اطلاعات درخواست',
          child: Column(
            children:
                rows
                    .map(
                      (row) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: _DetailRow(label: row.$1, value: row.$2),
                      ),
                    )
                    .toList(),
          ),
        ),
        if (notes.isNotEmpty) ...[
          const SizedBox(height: 12),
          _DetailSection(
            title: 'یادداشت‌ها',
            child: Column(
              children:
                  notes
                      .map(
                        (row) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _DetailRow(label: row.$1, value: row.$2),
                        ),
                      )
                      .toList(),
            ),
          ),
        ],
        const SizedBox(height: 12),
        _DetailSection(
          title: 'تاریخچه وضعیت',
          child:
              request.statusLogs.isEmpty
                  ? const Text('تغییر وضعیتی ثبت نشده است.')
                  : Column(
                    children:
                        request.statusLogs
                            .map((log) => _StatusLogTile(log: log))
                            .toList(),
                  ),
        ),
      ],
    );
  }
}

class _DetailSection extends StatelessWidget {
  const _DetailSection({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            child,
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 130,
          child: Text(label, style: Theme.of(context).textTheme.bodySmall),
        ),
        const SizedBox(width: 12),
        Expanded(child: Text(value)),
      ],
    );
  }
}

class _StatusLogTile extends StatelessWidget {
  const _StatusLogTile({required this.log});

  final AdminConsultRequestStatusLog log;

  @override
  Widget build(BuildContext context) {
    final change = [
      if (log.fromStatus != null) _statusLabel(log.fromStatus!),
      _statusLabel(log.toStatus),
    ].join(' ← ');

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(change),
                const SizedBox(height: 3),
                Text(
                  _compactDate(log.createdAt),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if (log.changedBy != null) ...[
                  const SizedBox(height: 3),
                  Text(
                    'تغییر توسط کاربر #${log.changedBy}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
                if (log.note != null && log.note!.trim().isNotEmpty) ...[
                  const SizedBox(height: 3),
                  Text(log.note!),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterBar extends StatelessWidget {
  const _FilterBar({
    required this.label,
    required this.value,
    required this.statuses,
    required this.onChanged,
  });

  final String label;
  final String? value;
  final List<String> statuses;
  final ValueChanged<String?>? onChanged;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            SizedBox(
              width: 280,
              child: DropdownButtonFormField<String>(
                initialValue: value ?? 'all',
                decoration: InputDecoration(
                  labelText: label,
                  border: const OutlineInputBorder(),
                ),
                items: [
                  const DropdownMenuItem(value: 'all', child: Text('همه')),
                  ...statuses.map(
                    (item) => DropdownMenuItem(
                      value: item,
                      child: Text(_statusLabel(item)),
                    ),
                  ),
                ],
                onChanged:
                    onChanged == null
                        ? null
                        : (value) => onChanged!(value == 'all' ? null : value),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final color = switch (status) {
      'approved' || 'completed' => colorScheme.primaryContainer,
      'pending_review' || 'open' => colorScheme.tertiaryContainer,
      'rejected' || 'cancelled' || 'suspended' => colorScheme.errorContainer,
      _ => colorScheme.surfaceContainerHighest,
    };

    return Chip(label: Text(_statusLabel(status)), backgroundColor: color);
  }
}

String _statusLabel(String status) {
  return switch (status) {
    'draft' => 'پیش‌نویس',
    'pending_review' => 'در انتظار بررسی',
    'approved' => 'تأیید شده',
    'rejected' => 'رد شده',
    'suspended' => 'تعلیق شده',
    'open' => 'باز',
    'accepted' => 'پذیرفته شده',
    'in_progress' => 'در حال انجام',
    'completed' => 'تکمیل شده',
    'cancelled' => 'لغو شده',
    _ => status,
  };
}

String _contactMethodLabel(String method) {
  return switch (method) {
    'in_app' => 'داخل اپلیکیشن',
    'phone' => 'تلفنی',
    'video' => 'تصویری',
    'visit' => 'حضوری',
    _ => method,
  };
}

String _compactDate(String value) {
  if (value.length < 10) return value;
  return value.substring(0, 10);
}
