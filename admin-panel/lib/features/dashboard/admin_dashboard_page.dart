import 'package:flutter/material.dart';

import '../../core/localization/admin_localizations.dart';
import '../../core/responsive/admin_responsive.dart';
import '../../core/widgets/admin_data_table.dart';
import '../../core/widgets/admin_status_chip.dart';

class AdminDashboardPage extends StatelessWidget {
  const AdminDashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AdminLocalizations.of(context);

    return AdminResponsiveBuilder(
      builder: (context, constraints, r) {
        return SingleChildScrollView(
          padding: r.pagePadding(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                l10n.dashboard,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 16,
                runSpacing: 16,
                children: const [
                  _MetricCard(title: 'کاربران', value: '۱۲۸'),
                  _MetricCard(title: 'فروشگاه‌ها', value: '۲۴'),
                  _MetricCard(title: 'محصولات', value: '۳۴۰'),
                  _MetricCard(title: 'پرداخت‌ها', value: '۱۸'),
                ],
              ),
              const SizedBox(height: 24),
              AdminDataTable(
                columns: const [
                  DataColumn(label: Text('بخش')),
                  DataColumn(label: Text('وضعیت')),
                  DataColumn(label: Text('توضیح')),
                ],
                rows: const [
                  DataRow(
                    cells: [
                      DataCell(Text('Backend')),
                      DataCell(AdminStatusChip(label: 'OK')),
                      DataCell(Text('Health فعال است')),
                    ],
                  ),
                  DataRow(
                    cells: [
                      DataCell(Text('Admin')),
                      DataCell(AdminStatusChip(label: 'Foundation')),
                      DataCell(Text('اسکلت پنل آماده است')),
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.title,
    required this.value,
  });

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title),
              const SizedBox(height: 12),
              Text(
                value,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
