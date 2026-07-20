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
  AdminReconciliation? _reconciliation;
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
    _checkReconciliation();
  }

  Future<void> _checkReconciliation() async {
    try {
      final result = await _repository.reconciliation();
      if (mounted) setState(() => _reconciliation = result);
    } on AdminFinanceApiException catch (e) {
      if (mounted) setState(() => _error = e.error.message);
    }
  }

  Future<void> _settlementAction(AdminFinanceRecord row, String action) async {
    try {
      if (action == 'simulate') {
        await _repository.simulatePayout(row.id);
      } else {
        await _repository.decideSettlement(row.id, action);
      }
      await _load(_result?.page ?? 1);
      await _checkReconciliation();
    } on AdminFinanceApiException catch (e) {
      if (mounted) setState(() => _error = e.error.message);
    }
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
              : Column(
                children: [
                  _reconciliationCard(),
                  Expanded(child: _buildContent()),
                ],
              ),
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
                DataColumn(label: Text('عملیات')),
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
                      DataCell(_actions(row)),
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

  Widget _reconciliationCard() {
    final row = _reconciliation;
    return Card(
      margin: const EdgeInsets.all(12),
      child: ListTile(
        leading: Icon(
          row?.clean == true ? Icons.check_circle : Icons.warning_amber,
          color: row?.clean == true ? Colors.green : Colors.orange,
        ),
        title: Text(
          row == null
              ? 'تطبیق دفتر کل'
              : row.clean
              ? 'تطبیق مالی سالم است'
              : 'مغایرت مالی نیازمند بررسی است',
        ),
        subtitle:
            row == null
                ? null
                : Text(
                  'پرداخت مفقود: ${row.missingPayments}، بازپرداخت مفقود: ${row.missingRefunds}، سند نامتوازن: ${row.unbalanced}',
                ),
        trailing: IconButton(
          onPressed: _checkReconciliation,
          icon: const Icon(Icons.refresh),
          tooltip: 'اجرای مجدد تطبیق',
        ),
      ),
    );
  }

  Widget _actions(AdminFinanceRecord row) {
    if (_resource != AdminFinanceResource.settlements) {
      return const Text('-');
    }
    if (row.status == 'requested') {
      return Wrap(
        children: [
          TextButton(
            onPressed: () => _settlementAction(row, 'approve'),
            child: const Text('تأیید'),
          ),
          TextButton(
            onPressed: () => _settlementAction(row, 'reject'),
            child: const Text('رد'),
          ),
        ],
      );
    }
    if (row.status == 'approved') {
      return TextButton(
        onPressed: () => _settlementAction(row, 'simulate'),
        child: const Text('تسویه شبیه‌سازی‌شده'),
      );
    }
    return const Text('-');
  }
}
