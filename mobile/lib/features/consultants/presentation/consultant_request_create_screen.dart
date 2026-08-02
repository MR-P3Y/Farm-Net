import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_glass_card.dart';
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
  final _formKey = GlobalKey<FormState>();

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
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'درخواست مشاوره',
          en: 'Consultation request',
        ),
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return detail.when(
              loading: () => const FarmLoadingView(),
              error:
                  (error, _) => Center(
                    child: Padding(
                      padding: r.pagePadding(),
                      child: Text(
                        context.l10n.tr(
                          fa: 'دریافت اطلاعات مشاور ناموفق بود.',
                          en: 'Could not load consultant information.',
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              data: (consultant) {
                return Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 720),
                    child: Form(
                      key: _formKey,
                      child: ListView(
                        padding: r.pagePadding(),
                        children: [
                          _RequestIntro(consultant: consultant),
                          SizedBox(height: r.v(10)),
                          _ConsultantSummary(consultant: consultant),
                          SizedBox(height: r.v(12)),
                          if (consultant.specialties.isNotEmpty) ...[
                            _SectionTitle(
                              icon: Icons.workspace_premium_outlined,
                              text: context.l10n.tr(
                                fa: 'موضوع مشاوره',
                                en: 'Consultation topic',
                              ),
                            ),
                            const SizedBox(height: 7),
                            Wrap(
                              spacing: 7,
                              runSpacing: 7,
                              children:
                                  consultant.specialties.map((specialty) {
                                    final selected =
                                        (_specialtyId ??
                                            consultant.specialties.first.id) ==
                                        specialty.id;
                                    return ChoiceChip(
                                      label: Text(specialty.title),
                                      selected: selected,
                                      onSelected:
                                          (_) => setState(
                                            () => _specialtyId = specialty.id,
                                          ),
                                    );
                                  }).toList(),
                            ),
                            SizedBox(height: r.v(12)),
                          ],
                          TextFormField(
                            controller: _titleController,
                            textInputAction: TextInputAction.next,
                            maxLength: 255,
                            decoration: InputDecoration(
                              labelText: context.l10n.tr(
                                fa: 'عنوان کوتاه مشکل',
                                en: 'Short issue title',
                              ),
                              hintText: context.l10n.tr(
                                fa: 'مثلاً زردشدن برگ‌های گوجه‌فرنگی',
                                en: 'Example: Tomato leaves are turning yellow',
                              ),
                            ),
                            validator:
                                (value) =>
                                    (value?.trim().length ?? 0) < 3
                                        ? context.l10n.tr(
                                          fa: 'حداقل ۳ نویسه وارد کنید.',
                                          en: 'Enter at least 3 characters.',
                                        )
                                        : null,
                          ),
                          SizedBox(height: r.v(12)),
                          TextFormField(
                            controller: _descriptionController,
                            minLines: 5,
                            maxLines: 10,
                            maxLength: 8000,
                            decoration: InputDecoration(
                              labelText: context.l10n.tr(
                                fa: 'شرح کامل مسئله',
                                en: 'Describe the issue',
                              ),
                              hintText: context.l10n.tr(
                                fa:
                                    'علائم، زمان شروع و اقداماتی که انجام داده‌اید را بنویسید.',
                                en:
                                    'Describe symptoms, when they started, and actions already taken.',
                              ),
                            ),
                            validator:
                                (value) =>
                                    (value?.trim().length ?? 0) < 10
                                        ? context.l10n.tr(
                                          fa:
                                              'برای بررسی بهتر حداقل ۱۰ نویسه بنویسید.',
                                          en: 'Enter at least 10 characters.',
                                        )
                                        : null,
                          ),
                          SizedBox(height: r.v(12)),
                          _SectionTitle(
                            icon: Icons.forum_outlined,
                            text: context.l10n.tr(
                              fa: 'روش ارتباط ترجیحی',
                              en: 'Preferred contact method',
                            ),
                          ),
                          const SizedBox(height: 7),
                          Wrap(
                            spacing: 7,
                            runSpacing: 7,
                            children:
                                [
                                      _ContactChoice(
                                        'in_app',
                                        Icons.chat_outlined,
                                        context.l10n.tr(
                                          fa: 'داخل اپ',
                                          en: 'In app',
                                        ),
                                      ),
                                      _ContactChoice(
                                        'phone',
                                        Icons.phone_outlined,
                                        context.l10n.tr(
                                          fa: 'تلفنی',
                                          en: 'Phone',
                                        ),
                                      ),
                                      _ContactChoice(
                                        'video',
                                        Icons.videocam_outlined,
                                        context.l10n.tr(
                                          fa: 'تصویری',
                                          en: 'Video',
                                        ),
                                      ),
                                      _ContactChoice(
                                        'visit',
                                        Icons.location_on_outlined,
                                        context.l10n.tr(
                                          fa: 'حضوری',
                                          en: 'On-site',
                                        ),
                                      ),
                                    ]
                                    .map(
                                      (item) => ChoiceChip(
                                        avatar: Icon(item.icon, size: 18),
                                        label: Text(item.label),
                                        selected: _contactMethod == item.value,
                                        onSelected:
                                            (_) => setState(
                                              () => _contactMethod = item.value,
                                            ),
                                      ),
                                    )
                                    .toList(),
                          ),
                          SizedBox(height: r.v(12)),
                          _PrivacyNote(),
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
                            label: Text(
                              context.l10n.tr(
                                fa: 'ثبت درخواست مشاوره',
                                en: 'Submit request',
                              ),
                            ),
                          ),
                        ],
                      ),
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

    if (!(_formKey.currentState?.validate() ?? false)) return;

    final created = await ref
        .read(consultantRequestControllerProvider.notifier)
        .createRequest(
          consultantProfileId: consultant.id,
          specialtyId: _specialtyId ?? consultant.specialties.firstOrNull?.id,
          title: title,
          description: description,
          contactMethod: _contactMethod,
        );

    if (!mounted || !created) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('درخواست مشاوره ثبت شد.')));
    context.pushReplacement('/consultants/requests');
  }
}

class _ContactChoice {
  const _ContactChoice(this.value, this.icon, this.label);
  final String value;
  final IconData icon;
  final String label;
}

class _RequestIntro extends StatelessWidget {
  const _RequestIntro({required this.consultant});
  final ConsultantProfileModel consultant;

  @override
  Widget build(BuildContext context) => FarmGlassCard(
    borderRadius: 22,
    padding: const EdgeInsets.all(14),
    child: Row(
      children: [
        Icon(
          Icons.lightbulb_outline_rounded,
          color: Theme.of(context).colorScheme.primary,
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            context.l10n.tr(
              fa:
                  'مسئله را روشن و دقیق بنویسید تا ${consultant.resolvedName} سریع‌تر راهنمایی کند.',
              en:
                  'Describe the issue clearly so ${consultant.resolvedName} can help faster.',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    ),
  );
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
      const SizedBox(width: 7),
      Expanded(
        child: Text(
          text,
          style: Theme.of(
            context,
          ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
        ),
      ),
    ],
  );
}

class _PrivacyNote extends StatelessWidget {
  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color: Theme.of(
        context,
      ).colorScheme.surfaceContainerHighest.withValues(alpha: .55),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.privacy_tip_outlined, size: 19),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              context.l10n.tr(
                fa: 'اطلاعات تماس حساس یا رمز عبور را در شرح درخواست وارد نکنید.',
                en:
                    'Do not include passwords or sensitive contact information in the description.',
              ),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    ),
  );
}

class _ConsultantSummary extends StatelessWidget {
  const _ConsultantSummary({required this.consultant});

  final ConsultantProfileModel consultant;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return FarmGlassCard(
      borderRadius: 22,
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 23,
                  backgroundImage:
                      absoluteApiUrl(consultant.avatarUrl) == null
                          ? null
                          : NetworkImage(absoluteApiUrl(consultant.avatarUrl)!),
                  child:
                      consultant.avatarUrl == null
                          ? const Icon(Icons.support_agent_outlined)
                          : null,
                ),
                const SizedBox(width: 10),
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
