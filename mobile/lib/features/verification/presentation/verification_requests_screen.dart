import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/verification_models.dart';
import '../state/verification_controller.dart';
import 'create_verification_screen.dart';

class VerificationRequestsScreen extends ConsumerStatefulWidget {
  const VerificationRequestsScreen({super.key});

  @override
  ConsumerState<VerificationRequestsScreen> createState() =>
      _VerificationRequestsScreenState();
}

class _VerificationRequestsScreenState
    extends ConsumerState<VerificationRequestsScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(verificationControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(verificationControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('درخواست‌های تأیید من'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const CreateVerificationScreen()),
          );
        },
        icon: const Icon(Icons.add),
        label: const Text('درخواست جدید'),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return const FarmLoadingView();
          }

          if (state.errorMessage != null && state.requests.isEmpty) {
            return Center(
              child: Padding(
                padding: r.pagePadding(),
                child: Text(
                  state.errorMessage!,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            );
          }

          if (state.requests.isEmpty) {
            return Center(
              child: Padding(
                padding: r.pagePadding(),
                child: const Text('هنوز درخواست تأییدی ثبت نکرده‌اید.'),
              ),
            );
          }

          return ListView.separated(
            padding: r.pagePadding(),
            itemCount: state.requests.length,
            separatorBuilder: (_, _) => SizedBox(height: r.v(12)),
            itemBuilder: (context, index) {
              final item = state.requests[index];
              return _VerificationCard(item: item);
            },
          );
        },
      ),
    );
  }
}

class _VerificationCard extends StatelessWidget {
  const _VerificationCard({required this.item});

  final VerificationRequest item;

  String _roleLabel(String role) {
    switch (role) {
      case 'shop_owner':
        return 'فروشگاه‌دار';
      case 'lessor':
        return 'موجر ادوات';
      case 'consultant':
        return 'مشاور';
      case 'service_provider':
        return 'ارائه‌دهنده خدمات';
      case 'data_client':
        return 'مشتری داده';
      default:
        return role;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'draft':
        return 'پیش‌نویس';
      case 'submitted':
        return 'ارسال‌شده';
      case 'under_review':
        return 'در حال بررسی';
      case 'needs_revision':
        return 'نیازمند اصلاح';
      case 'approved':
        return 'تأیید شده';
      case 'rejected':
        return 'رد شده';
      case 'cancelled':
        return 'لغو شده';
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.verified_user_outlined),
        title: Text(_roleLabel(item.targetRole)),
        subtitle: Text(
          'وضعیت: ${_statusLabel(item.status)}\n'
          'مدارک: ${item.documents.length}',
        ),
        isThreeLine: true,
        trailing: Text(
          '#${item.id}',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }
}
