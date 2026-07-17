import 'package:flutter/material.dart';

import '../../../core/widgets/admin_empty_view.dart';
import '../../../core/widgets/admin_error_view.dart';
import '../../../core/widgets/admin_loading_view.dart';
import '../data/admin_finance_api.dart';
import '../data/admin_finance_models.dart';
import '../data/admin_finance_repository.dart';

class AdminFinancePage extends StatefulWidget {
  const AdminFinancePage({super.key});
  @override
  State<AdminFinancePage> createState() => _AdminFinancePageState();
}

class _AdminFinancePageState extends State<AdminFinancePage>
    with SingleTickerProviderStateMixin {
  final _repository = AdminFinanceRepository();
  late final TabController _tabs;
  AdminFinancePageResult? _result;
  String? _error;
  bool _loading = true;
  AdminFinanceResource get _resource =>
      AdminFinanceResource.values[_tabs.index];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(
      length: AdminFinanceResource.values.length,
      vsync: this,
    )..addListener(() {
      if (!_tabs.indexIsChanging) _load(1);
    });
    _load(1);
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load(int page) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await _repository.list(_resource, page: page);
      if (mounted) setState(() => _result = result);
    } on AdminFinanceApiException catch (e) {
      if (mounted) setState(() => _error = e.error.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت مالی'),
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabs: [
            for (final r in AdminFinanceResource.values) Tab(text: r.label),
          ],
        ),
      ),
      body:
          _loading
              ? const AdminLoadingView()
              : _error != null
              ? AdminErrorView(
                message: _error!,
                onRetry: () => _load(_result?.page ?? 1),
              )
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    final result = _result;
    if (result == null || result.items.isEmpty) {
      return const AdminEmptyView(message: 'رکورد مالی یافت نشد.');
    }
    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: const [
                DataColumn(label: Text('شناسه')),
                DataColumn(label: Text('عنوان')),
                DataColumn(label: Text('وضعیت')),
                DataColumn(label: Text('مبلغ')),
                DataColumn(label: Text('مرجع')),
                DataColumn(label: Text('تاریخ')),
              ],
              rows: [
                for (final row in result.items)
                  DataRow(
                    cells: [
                      DataCell(Text('${row.id}')),
                      DataCell(Text(row.title)),
                      DataCell(Text(row.status)),
                      DataCell(Text(row.amount?.toString() ?? '-')),
                      DataCell(Text(row.reference ?? '-')),
                      DataCell(
                        Text(row.createdAt?.toLocal().toString() ?? '-'),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed:
                    result.page > 1 ? () => _load(result.page - 1) : null,
                icon: const Icon(Icons.chevron_right),
              ),
              Text(
                'صفحه ${result.page} از ${result.totalPages} — ${result.total} رکورد',
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
        ),
      ],
    );
  }
}
