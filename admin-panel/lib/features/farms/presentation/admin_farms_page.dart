import 'package:flutter/material.dart';

import '../data/admin_farm_api.dart';
import '../data/admin_farm_models.dart';

class AdminFarmsPage extends StatefulWidget {
  const AdminFarmsPage({super.key});

  @override
  State<AdminFarmsPage> createState() => _AdminFarmsPageState();
}

class _AdminFarmsPageState extends State<AdminFarmsPage> {
  final _api = AdminFarmApi();
  final _search = TextEditingController();
  AdminFarmPage? _result;
  bool _loading = true;
  String? _error;
  String? _status;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _load([int page = 1]) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await _api.list(
        query: _search.text.trim(),
        status: _status,
        page: page,
      );
      if (mounted) setState(() => _result = result);
    } on AdminFarmApiException catch (error) {
      if (mounted) setState(() => _error = error.error.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Text(
                'پشتیبانی مزارع',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const Spacer(),
              IconButton(
                tooltip: 'تازه‌سازی',
                onPressed: _loading ? null : _load,
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
                width: 320,
                child: TextField(
                  controller: _search,
                  decoration: const InputDecoration(
                    labelText: 'نام یا شناسه مزرعه',
                    prefixIcon: Icon(Icons.search),
                    border: OutlineInputBorder(),
                  ),
                  onSubmitted: (_) => _load(),
                ),
              ),
              SizedBox(
                width: 180,
                child: DropdownButtonFormField<String?>(
                  initialValue: _status,
                  decoration: const InputDecoration(
                    labelText: 'وضعیت',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: null, child: Text('همه')),
                    DropdownMenuItem(value: 'active', child: Text('فعال')),
                    DropdownMenuItem(value: 'archived', child: Text('بایگانی')),
                  ],
                  onChanged: (value) {
                    _status = value;
                    _load();
                  },
                ),
              ),
              FilledButton.icon(
                onPressed: _loading ? null : _load,
                icon: const Icon(Icons.filter_alt_outlined),
                label: const Text('اعمال'),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
          const SizedBox(height: 16),
          Expanded(child: _body()),
        ],
      ),
    );
  }

  Widget _body() {
    if (_loading) return const Center(child: CircularProgressIndicator());
    final result = _result;
    if (result == null || result.items.isEmpty) {
      return const Center(child: Text('مزرعه‌ای یافت نشد.'));
    }
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('شناسه')),
                  DataColumn(label: Text('مالک')),
                  DataColumn(label: Text('نام')),
                  DataColumn(label: Text('وضعیت')),
                  DataColumn(label: Text('مساحت (مترمربع)')),
                  DataColumn(label: Text('قطعه')),
                  DataColumn(label: Text('دوره کشت')),
                  DataColumn(label: Text('عملیات')),
                ],
                rows:
                    result.items
                        .map(
                          (farm) => DataRow(
                            cells: [
                              DataCell(Text('${farm.id}')),
                              DataCell(Text('${farm.ownerUserId}')),
                              DataCell(Text(farm.name)),
                              DataCell(Text(farm.status)),
                              DataCell(
                                Text(
                                  farm.declaredAreaSqm?.toStringAsFixed(0) ??
                                      '-',
                                ),
                              ),
                              DataCell(Text('${farm.plotsCount}')),
                              DataCell(Text('${farm.cyclesCount}')),
                              DataCell(
                                TextButton(
                                  onPressed: () => _showDetail(farm.id),
                                  child: const Text('مشاهده'),
                                ),
                              ),
                            ],
                          ),
                        )
                        .toList(),
              ),
            ),
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              onPressed: result.page > 1 ? () => _load(result.page - 1) : null,
              icon: const Icon(Icons.chevron_right),
            ),
            Text(
              'صفحه ${result.page} از ${result.totalPages} — ${result.total} مورد',
            ),
            IconButton(
              onPressed:
                  result.page < result.totalPages
                      ? () => _load(result.page + 1)
                      : null,
              icon: const Icon(Icons.chevron_left),
            ),
          ],
        ),
      ],
    );
  }

  Future<void> _showDetail(int farmId) async {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );
    try {
      final values = await Future.wait([
        _api.detail(farmId),
        _api.audit(farmId),
      ]);
      if (!mounted) return;
      Navigator.pop(context);
      await showDialog<void>(
        context: context,
        builder:
            (_) => _FarmDetailDialog(
              detail: values[0] as AdminFarmDetail,
              audit: values[1] as List<AdminFarmAudit>,
            ),
      );
    } on AdminFarmApiException catch (error) {
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.error.message)));
    }
  }
}

class _FarmDetailDialog extends StatelessWidget {
  const _FarmDetailDialog({required this.detail, required this.audit});

  final AdminFarmDetail detail;
  final List<AdminFarmAudit> audit;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${detail.summary.name} (#${detail.summary.id})'),
      content: SizedBox(
        width: 900,
        height: 620,
        child: ListView(
          children: [
            Text(
              'مالک: ${detail.summary.ownerUserId} | وضعیت: ${detail.summary.status}',
            ),
            const SizedBox(height: 16),
            Text('قطعه‌ها', style: Theme.of(context).textTheme.titleMedium),
            ...detail.plots.map(
              (plot) => ListTile(
                leading: const Icon(Icons.landscape_outlined),
                title: Text(
                  '${plot.name} — ${plot.areaSqm.toStringAsFixed(0)} مترمربع',
                ),
                subtitle: Text(
                  'وضعیت: ${plot.status} | استان: ${plot.provinceId ?? '-'} | شهر: ${plot.cityId ?? '-'} | دوره‌ها: ${plot.cyclesCount}',
                ),
              ),
            ),
            const Divider(),
            Text(
              'دوره‌های کشت',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            ...detail.cycles.map(
              (cycle) => ListTile(
                leading: const Icon(Icons.grass_outlined),
                title: Text(cycle.title ?? 'دوره #${cycle.id}'),
                subtitle: Text(
                  'محصول: ${cycle.cropId} | وضعیت: ${cycle.status} | شروع برنامه: ${cycle.plannedStartDate}',
                ),
              ),
            ),
            const Divider(),
            Text(
              'رویدادهای ممیزی',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (audit.isEmpty)
              const ListTile(title: Text('رویدادی ثبت نشده است.')),
            ...audit.map(
              (item) => ListTile(
                leading: const Icon(Icons.history),
                title: Text(item.action),
                subtitle: Text(
                  '${item.targetType} #${item.targetId} | کاربر ${item.actorUserId} | ${item.createdAt}',
                ),
              ),
            ),
          ],
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
