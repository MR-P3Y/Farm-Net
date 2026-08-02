import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../reviews/presentation/public_reviews_section.dart';
import '../data/consultant_models.dart';
import '../data/consultant_repository.dart';

final consultantDetailProvider =
    FutureProvider.family<ConsultantProfileModel, int>((ref, profileId) {
      return ref.watch(consultantRepositoryProvider).detail(profileId);
    });

class ConsultantDetailScreen extends ConsumerWidget {
  const ConsultantDetailScreen({required this.profileId, super.key});

  final int profileId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(consultantDetailProvider(profileId));

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'پروفایل مشاور', en: 'Consultant profile'),
        actions: [
          IconButton(
            tooltip: context.l10n.tr(fa: 'درخواست‌های من', en: 'My requests'),
            onPressed: () => context.push('/consultants/requests'),
            icon: const Icon(Icons.assignment_outlined),
          ),
        ],
      ),
      bottomNavigationBar:
          detail.asData == null
              ? null
              : SafeArea(
                minimum: const EdgeInsets.fromLTRB(16, 8, 16, 12),
                child: FilledButton.icon(
                  onPressed:
                      () => context.push(
                        '/consultants/${detail.asData!.value.id}/request',
                      ),
                  icon: const Icon(Icons.chat_bubble_outline_rounded),
                  label: Text(
                    context.l10n.tr(
                      fa: 'درخواست مشاوره',
                      en: 'Request consultation',
                    ),
                  ),
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
                final avatarUrl = absoluteApiUrl(consultant.avatarUrl);

                return SingleChildScrollView(
                  padding: r.pagePadding(),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 720),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          FarmGlassCard(
                            borderRadius: 28,
                            child: Padding(
                              padding: EdgeInsets.all(r.s(20)),
                              child: Column(
                                children: [
                                  _Avatar(url: avatarUrl, size: r.s(92)),
                                  SizedBox(height: r.v(14)),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Flexible(
                                        child: Text(
                                          consultant.resolvedName,
                                          textAlign: TextAlign.center,
                                          style:
                                              Theme.of(
                                                context,
                                              ).textTheme.headlineSmall,
                                        ),
                                      ),
                                      if (consultant.isVerified) ...[
                                        const SizedBox(width: 6),
                                        Icon(
                                          Icons.verified,
                                          color:
                                              Theme.of(
                                                context,
                                              ).colorScheme.primary,
                                        ),
                                      ],
                                    ],
                                  ),
                                  if ((consultant.title ?? '').isNotEmpty) ...[
                                    SizedBox(height: r.v(6)),
                                    Text(
                                      consultant.title!,
                                      textAlign: TextAlign.center,
                                      style:
                                          Theme.of(
                                            context,
                                          ).textTheme.titleMedium,
                                    ),
                                  ],
                                  SizedBox(height: r.v(12)),
                                  Wrap(
                                    alignment: WrapAlignment.center,
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: [
                                      _InfoChip(
                                        icon: Icons.star_rounded,
                                        label: context.l10n.tr(
                                          fa:
                                              'امتیاز ${toPersianDigits(consultant.ratingAverage.toStringAsFixed(1))}',
                                          en:
                                              'Rating ${consultant.ratingAverage.toStringAsFixed(1)}',
                                        ),
                                      ),
                                      _InfoChip(
                                        icon: Icons.rate_review_outlined,
                                        label: context.l10n.tr(
                                          fa:
                                              '${toPersianDigits(consultant.reviewsCount)} نظر',
                                          en:
                                              '${consultant.reviewsCount} reviews',
                                        ),
                                      ),
                                      _InfoChip(
                                        icon: Icons.place_outlined,
                                        label: _location(context, consultant),
                                      ),
                                      if (consultant.experienceYears != null)
                                        _InfoChip(
                                          icon: Icons.work_outline,
                                          label: context.l10n.tr(
                                            fa:
                                                '${toPersianDigits(consultant.experienceYears)} سال تجربه',
                                            en:
                                                '${consultant.experienceYears} years experience',
                                          ),
                                        ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                          SizedBox(height: r.v(12)),
                          if (consultant.specialties.isNotEmpty)
                            _SectionCard(
                              icon: Icons.workspace_premium_outlined,
                              title: context.l10n.tr(
                                fa: 'حوزه‌های تخصصی',
                                en: 'Areas of expertise',
                              ),
                              child: Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children:
                                    consultant.specialties
                                        .map(
                                          (item) => Chip(
                                            label: Text(item.title),
                                            avatar: const Icon(
                                              Icons.eco_outlined,
                                              size: 18,
                                            ),
                                          ),
                                        )
                                        .toList(),
                              ),
                            ),
                          if ((consultant.bio ?? '').isNotEmpty) ...[
                            SizedBox(height: r.v(12)),
                            _SectionCard(
                              icon: Icons.person_outline_rounded,
                              title: context.l10n.tr(
                                fa: 'درباره مشاور',
                                en: 'About the consultant',
                              ),
                              child: Text(
                                consultant.bio!,
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                            ),
                          ],
                          SizedBox(height: r.v(12)),
                          _SectionCard(
                            icon: Icons.insights_outlined,
                            title: context.l10n.tr(
                              fa: 'عملکرد مشاوره',
                              en: 'Consultation performance',
                            ),
                            child: Column(
                              children: [
                                _MetricRow(
                                  label: context.l10n.tr(
                                    fa: 'کل درخواست‌ها',
                                    en: 'Total requests',
                                  ),
                                  value: consultant.requestsCount,
                                ),
                                const Divider(height: 20),
                                _MetricRow(
                                  label: context.l10n.tr(
                                    fa: 'مشاوره‌های تکمیل‌شده',
                                    en: 'Completed consultations',
                                  ),
                                  value: consultant.completedRequestsCount,
                                ),
                              ],
                            ),
                          ),
                          SizedBox(height: r.v(12)),
                          PublicReviewsSection(
                            subjectType: 'consultant',
                            subjectId: consultant.id,
                          ),
                          SizedBox(height: r.v(12)),
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

  String _location(BuildContext context, ConsultantProfileModel value) {
    final parts =
        [
          value.cityName,
          value.provinceName,
        ].where((item) => item?.trim().isNotEmpty == true).cast<String>();
    return parts.isEmpty
        ? context.l10n.tr(fa: 'موقعیت ثبت نشده', en: 'Location unavailable')
        : parts.join(context.l10n.isFa ? '، ' : ', ');
  }
}

class _Avatar extends StatelessWidget {
  const _Avatar({required this.url, required this.size});

  final String? url;
  final double size;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return SizedBox.square(
      dimension: size,
      child: DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: colors.primaryContainer,
        ),
        child: ClipOval(
          child:
              url == null
                  ? Icon(
                    Icons.support_agent_outlined,
                    size: size * .52,
                    color: colors.onPrimaryContainer,
                  )
                  : Image.network(
                    url!,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) {
                      return Icon(
                        Icons.support_agent_outlined,
                        size: size * .52,
                        color: colors.onPrimaryContainer,
                      );
                    },
                  ),
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 18),
      label: Text(label),
      visualDensity: VisualDensity.compact,
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
    required this.icon,
    required this.title,
    required this.child,
  });

  final IconData icon;
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return FarmGlassCard(
      borderRadius: 22,
      child: Padding(
        padding: const EdgeInsets.all(4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  size: 21,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  const _MetricRow({required this.label, required this.value});

  final String label;
  final int value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Text(label)),
        Text(
          toPersianDigits(value),
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ],
    );
  }
}
