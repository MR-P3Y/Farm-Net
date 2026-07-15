import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/consultant_models.dart';
import '../state/consultant_request_controller.dart';
import 'consultant_detail_screen.dart';

class ConsultantRequestCreateScreen extends ConsumerStatefulWidget {
  const ConsultantRequestCreateScreen({
    required this.consultantProfileId,
    super.key,
  });

  final int consultantProfileId;

  @override
  ConsumerState<ConsultantRequestCreateScreen> createState() =>
      _ConsultantRequestCreateScreenState();
}

class _ConsultantRequestCreateScreenState
    extends ConsumerState<ConsultantRequestCreateScreen> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  int? _specialtyId;
  String _contactMethod = 'in_app';

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final detail = ref.watch(
      consultantDetailProvider(widget.consultantProfileId),
    );
    final requestState = ref.watch(consultantRequestControllerProvider);

    return Scaffold(
      appBar: const FarmAppBar(title: 'درخواست مشاوره'),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return detail.when(
              loading: () => const FarmLoadingView(),
              error:
                  (error, _) => Center(
                    child: Padding(
                      padding: r.pagePadding(),
                      child: const Text(
                        'دریافت اطلاعات مشاور ناموفق بود.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              data: (consultant) {
                return Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 720),
                    child: ListView(
                      padding: r.pagePadding(),
                      children: [
                        _ConsultantSummary(consultant: consultant),
                        SizedBox(height: r.v(12)),
                        if (consultant.specialties.isNotEmpty) ...[
                          DropdownButtonFormField<int>(
                            initialValue: _specialtyId,
                            decoration: const InputDecoration(
                              labelText: 'تخصص مرتبط',
                              border: OutlineInputBorder(),
                            ),
                            items:
                                consultant.specialties
                                    .map(
                                      (specialty) => DropdownMenuItem(
                                        value: specialty.id,
                                        child: Text(specialty.title),
                                      ),
                                    )
                                    .toList(),
                            onChanged: (value) {
                              setState(() => _specialtyId = value);
                            },
                          ),
                          SizedBox(height: r.v(12)),
                        ],
                        TextField(
                          controller: _titleController,
                          textInputAction: TextInputAction.next,
                          decoration: const InputDecoration(
                            labelText: 'عنوان درخواست',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        TextField(
                          controller: _descriptionController,
                          minLines: 5,
                          maxLines: 10,
                          decoration: const InputDecoration(
                            labelText: 'شرح مشکل یا نیاز',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<String>(
                          initialValue: _contactMethod,
                          decoration: const InputDecoration(
                            labelText: 'روش ارتباط',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'in_app',
                              child: Text('داخل اپلیکیشن'),
                            ),
                            DropdownMenuItem(
                              value: 'phone',
                              child: Text('تماس تلفنی'),
                            ),
                            DropdownMenuItem(
                              value: 'video',
                              child: Text('تماس تصویری'),
                            ),
                            DropdownMenuItem(
                              value: 'visit',
                              child: Text('بازدید حضوری'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _contactMethod = value);
                          },
                        ),
                        if (requestState.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          _MessageBox(
                            message: requestState.errorMessage!,
                            isError: true,
                          ),
                        ],
                        SizedBox(height: r.v(16)),
                        FilledButton.icon(
                          onPressed:
                              requestState.isSaving
                                  ? null
                                  : () => _submit(consultant),
                          icon: const Icon(Icons.send_outlined),
                          label: const Text('ثبت درخواست'),
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }

  Future<void> _submit(ConsultantProfileModel consultant) async {
    final title = _titleController.text.trim();
    final description = _descriptionController.text.trim();

    if (title.length < 3 || description.length < 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('عنوان و شرح درخواست را کامل وارد کنید.')),
      );
      return;
    }

    final created = await ref
        .read(consultantRequestControllerProvider.notifier)
        .createRequest(
          consultantProfileId: consultant.id,
          specialtyId: _specialtyId,
          title: title,
          description: description,
          contactMethod: _contactMethod,
        );

    if (!mounted || !created) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('درخواست مشاوره ثبت شد.')));
    context.go('/consultants/requests');
  }
}

class _ConsultantSummary extends StatelessWidget {
  const _ConsultantSummary({required this.consultant});

  final ConsultantProfileModel consultant;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.support_agent_outlined),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    consultant.resolvedName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                if (consultant.isVerified)
                  Icon(
                    Icons.verified,
                    size: 20,
                    color: theme.colorScheme.primary,
                  ),
              ],
            ),
            if ((consultant.title ?? '').trim().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(consultant.title!),
            ],
          ],
        ),
      ),
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
