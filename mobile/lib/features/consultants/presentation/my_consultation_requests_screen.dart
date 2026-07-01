import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/consultant_models.dart';
import '../state/consultant_request_controller.dart';

class MyConsultationRequestsScreen extends ConsumerStatefulWidget {
  const MyConsultationRequestsScreen({super.key});

  @override
  ConsumerState<MyConsultationRequestsScreen> createState() =>
      _MyConsultationRequestsScreenState();
}

class _MyConsultationRequestsScreenState
    extends ConsumerState<MyConsultationRequestsScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(consultantRequestControllerProvider.notifier).loadMyRequests();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantRequestControllerProvider);

    return Scaffold(
      appBar: const FarmAppBar(title: 'درخواست‌های مشاوره من'),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            if (state.isLoading) {
              return const FarmLoadingView();
            }

            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (state.isSaving) const LinearProgressIndicator(),
                      if (state.errorMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _MessageBox(
                          message: state.errorMessage!,
                          isError: true,
                        ),
                      ],
                      if (state.successMessage != null) ...[
                        SizedBox(height: r.v(12)),
                        _MessageBox(
                          message: state.successMessage!,
                          isError: false,
                        ),
                      ],
                      SizedBox(height: r.v(12)),
                      Expanded(
                        child: RefreshIndicator(
                          onRefresh:
                              () =>
                                  ref
                                      .read(
                                        consultantRequestControllerProvider
                                            .notifier,
                                      )
                                      .loadMyRequests(),
                          child:
                              state.requests.isEmpty
                                  ? ListView(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    children: [
                                      SizedBox(height: r.v(120)),
                                      const FarmEmptyView(
                                        message:
                                            'هنوز درخواست مشاوره‌ای ثبت نکرده‌اید.',
                                      ),
                                    ],
                                  )
                                  : ListView.separated(
                                    physics:
                                        const AlwaysScrollableScrollPhysics(),
                                    itemCount: state.requests.length,
                                    separatorBuilder:
                                        (_, __) => SizedBox(height: r.v(10)),
                                    itemBuilder: (context, index) {
                                      final request = state.requests[index];
                                      return _RequestCard(
                                        request: request,
                                        onTap:
                                            () => context.push(
                                              '/consultants/requests/${request.id}',
                                            ),
                                        onCancel:
                                            request.canCancel && !state.isSaving
                                                ? () => _confirmCancel(request)
                                                : null,
                                      );
                                    },
                                  ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _confirmCancel(ConsultationRequestModel request) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('لغو درخواست'),
          content: Text('درخواست «${request.title}» لغو شود؟'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('لغو درخواست'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    await ref
        .read(consultantRequestControllerProvider.notifier)
        .cancelRequest(request.id);
  }
}

class _RequestCard extends StatelessWidget {
  const _RequestCard({
    required this.request,
    required this.onTap,
    required this.onCancel,
  });

  final ConsultationRequestModel request;
  final VoidCallback onTap;
  final VoidCallback? onCancel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final consultantName = request.consultant?.resolvedName;
    final subtitleParts = [
      if (consultantName != null && consultantName.trim().isNotEmpty)
        consultantName,
      if (request.specialty?.title.trim().isNotEmpty == true)
        request.specialty!.title,
      _contactMethodLabel(request.contactMethod),
    ];

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      request.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleMedium,
                    ),
                  ),
                  const SizedBox(width: 8),
                  _StatusChip(status: request.status),
                ],
              ),
              if (subtitleParts.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  subtitleParts.join(' • '),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const SizedBox(height: 8),
              Text(
                request.description,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Icon(
                    Icons.schedule_outlined,
                    size: 18,
                    color: theme.colorScheme.outline,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      _compactDate(request.createdAt),
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                  if (onCancel != null)
                    TextButton.icon(
                      onPressed: onCancel,
                      icon: const Icon(Icons.cancel_outlined),
                      label: const Text('لغو'),
                    ),
                ],
              ),
            ],
          ),
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
    final colors = Theme.of(context).colorScheme;

    final color = switch (status) {
      'open' => colors.primaryContainer,
      'accepted' => colors.secondaryContainer,
      'in_progress' => colors.tertiaryContainer,
      'completed' => colors.surfaceContainerHighest,
      'cancelled' => colors.errorContainer,
      'rejected' => colors.errorContainer,
      _ => colors.surfaceContainerHighest,
    };

    return Chip(
      label: Text(_statusLabel(status)),
      backgroundColor: color,
      visualDensity: VisualDensity.compact,
    );
  }
}

class _MessageBox extends StatelessWidget {
  const _MessageBox({required this.message, required this.isError});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: isError ? colors.errorContainer : colors.primaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(
          message,
          style: TextStyle(
            color:
                isError ? colors.onErrorContainer : colors.onPrimaryContainer,
          ),
        ),
      ),
    );
  }
}

String _statusLabel(String status) {
  return switch (status) {
    'open' => 'باز',
    'accepted' => 'پذیرفته‌شده',
    'in_progress' => 'در حال انجام',
    'completed' => 'تکمیل‌شده',
    'cancelled' => 'لغوشده',
    'rejected' => 'ردشده',
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
  if (value.length < 10) return toPersianDigits(value);
  return toPersianDigits(value.substring(0, 10));
}
