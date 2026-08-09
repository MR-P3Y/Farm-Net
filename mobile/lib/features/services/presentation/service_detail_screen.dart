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
import '../../../core/widgets/farm_primary_action_bar.dart';
import '../../favorites/data/favorite_models.dart';
import '../../favorites/presentation/favorite_button.dart';
import '../../reviews/presentation/public_reviews_section.dart';
import '../data/service_models.dart';
import '../state/service_discovery_controller.dart';
import 'service_ui.dart';
import 'service_request_badge.dart';

class ServiceDetailScreen extends ConsumerWidget {
  const ServiceDetailScreen({required this.offerId, super.key});

  final int offerId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(serviceOfferDetailProvider(offerId));
    final offer = detail.asData?.value;

    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'جزئیات خدمت', en: 'Service details'),
        fallbackLocation: '/services',
        actions: [
          FavoriteIconButton(
            subjectType: FavoriteSubjectType.serviceOffer,
            subjectId: offerId,
          ),
          const MyServiceRequestsAction(),
        ],
      ),
      bottomNavigationBar:
          offer == null
              ? null
              : FarmPrimaryActionBar(
                key: const Key('service-request-floating-button'),
                onPressed:
                    offer.provider?.acceptingRequests == false ||
                            offer.provider?.availabilityStatus == 'unavailable'
                        ? null
                        : () => context.push('/services/${offer.id}/request'),
                icon: Icons.post_add_rounded,
                label: context.l10n.tr(
                  fa:
                      offer.provider?.acceptingRequests == false ||
                              offer.provider?.availabilityStatus ==
                                  'unavailable'
                          ? 'فعلاً امکان ثبت درخواست نیست'
                          : 'ثبت درخواست این خدمت',
                  en:
                      offer.provider?.acceptingRequests == false ||
                              offer.provider?.availabilityStatus ==
                                  'unavailable'
                          ? 'Requests are temporarily unavailable'
                          : 'Request this service',
                ),
              ),
      body: SafeArea(
        child: detail.when(
          loading: () => const FarmLoadingView(),
          error:
              (_, __) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.cloud_off_outlined,
                        size: 48,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        context.l10n.tr(
                          fa: 'دریافت جزئیات خدمت ناموفق بود.',
                          en: 'Could not load service details.',
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed:
                            () => ref.invalidate(
                              serviceOfferDetailProvider(offerId),
                            ),
                        icon: const Icon(Icons.refresh),
                        label: Text(context.l10n.retry),
                      ),
                    ],
                  ),
                ),
              ),
          data: (offer) => ServiceDetailContent(offer: offer),
        ),
      ),
    );
  }
}

class ServiceDetailContent extends StatelessWidget {
  const ServiceDetailContent({required this.offer, super.key});

  final ServiceOffer offer;

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder:
          (context, constraints, r) => SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 760),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _ServiceHero(offer: offer),
                    SizedBox(height: r.v(14)),
                    _ServiceFacts(offer: offer),
                    if ((offer.description ?? '').isNotEmpty) ...[
                      SizedBox(height: r.v(14)),
                      _SectionCard(
                        icon: Icons.notes_rounded,
                        title: context.l10n.tr(
                          fa: 'درباره این خدمت',
                          en: 'About this service',
                        ),
                        child: Text(
                          offer.description!,
                          style: Theme.of(
                            context,
                          ).textTheme.bodyLarge?.copyWith(height: 1.75),
                        ),
                      ),
                    ],
                    if (offer.provider != null) ...[
                      SizedBox(height: r.v(14)),
                      _ProviderCard(provider: offer.provider!),
                    ],
                    SizedBox(height: r.v(14)),
                    PublicReviewsSection(
                      subjectType: 'service_offer',
                      subjectId: offer.id,
                    ),
                  ],
                ),
              ),
            ),
          ),
    );
  }
}

class _ServiceHero extends StatelessWidget {
  const _ServiceHero({required this.offer});

  final ServiceOffer offer;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return FarmGlassCard(
      borderRadius: 28,
      padding: EdgeInsets.zero,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Gallery(media: offer.media, category: offer.category),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: colors.primaryContainer,
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            serviceCategoryIcon(offer.category),
                            size: 17,
                            color: colors.primary,
                          ),
                          const SizedBox(width: 5),
                          Text(
                            offer.category?.title ??
                                context.l10n.tr(
                                  fa: 'خدمات کشاورزی',
                                  en: 'Agricultural service',
                                ),
                            style: Theme.of(
                              context,
                            ).textTheme.labelMedium?.copyWith(
                              color: colors.primary,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Spacer(),
                    if (offer.provider?.isVerified == true)
                      Tooltip(
                        message: context.l10n.tr(
                          fa: 'ارائه‌دهنده تأییدشده',
                          en: 'Verified provider',
                        ),
                        child: Icon(
                          Icons.verified_rounded,
                          color: colors.primary,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 14),
                Text(
                  offer.title,
                  key: const Key('service-professional-title'),
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w900,
                    height: 1.35,
                  ),
                ),
                if ((offer.shortDescription ?? '').isNotEmpty) ...[
                  const SizedBox(height: 9),
                  Text(
                    offer.shortDescription!,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: colors.onSurfaceVariant,
                      height: 1.55,
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 12,
                  ),
                  decoration: BoxDecoration(
                    color: colors.primary.withValues(alpha: .09),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: colors.primary.withValues(alpha: .18),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.payments_outlined, color: colors.primary),
                      const SizedBox(width: 9),
                      Expanded(
                        child: Text(
                          servicePriceLabel(context, offer),
                          style: Theme.of(
                            context,
                          ).textTheme.titleMedium?.copyWith(
                            color: colors.primary,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Gallery extends StatefulWidget {
  const _Gallery({required this.media, required this.category});

  final List<ServiceMedia> media;
  final ServiceCategory? category;

  @override
  State<_Gallery> createState() => _GalleryState();
}

class _GalleryState extends State<_Gallery> {
  int _page = 0;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final items = widget.media;
    return ClipRRect(
      borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
      child: SizedBox(
        height: 260,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (items.isEmpty)
              DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topRight,
                    end: Alignment.bottomLeft,
                    colors: [colors.primaryContainer, colors.tertiaryContainer],
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      serviceCategoryIcon(widget.category),
                      size: 72,
                      color: colors.primary,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      context.l10n.tr(
                        fa: 'خدمت کشاورزی حرفه‌ای',
                        en: 'Professional farm service',
                      ),
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: colors.onPrimaryContainer,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              )
            else
              PageView.builder(
                itemCount: items.length,
                onPageChanged: (value) => setState(() => _page = value),
                itemBuilder: (context, index) {
                  final item = items[index];
                  final url = absoluteApiUrl(item.displayUrl);
                  return Stack(
                    fit: StackFit.expand,
                    children: [
                      if (url == null)
                        ColoredBox(
                          color: colors.primaryContainer,
                          child: Icon(
                            Icons.image_outlined,
                            size: 72,
                            color: colors.primary,
                          ),
                        )
                      else
                        Image.network(
                          url,
                          fit: BoxFit.cover,
                          semanticLabel: item.altText,
                          errorBuilder:
                              (_, __, ___) => ColoredBox(
                                color: colors.primaryContainer,
                                child: Icon(
                                  Icons.broken_image_outlined,
                                  size: 72,
                                  color: colors.primary,
                                ),
                              ),
                        ),
                      if (item.portfolioStage != null)
                        PositionedDirectional(
                          start: 12,
                          bottom: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: .68),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: Text(
                              context.l10n.tr(
                                fa:
                                    item.portfolioStage == 'before'
                                        ? 'قبل از اجرا'
                                        : 'بعد از اجرا',
                                en:
                                    item.portfolioStage == 'before'
                                        ? 'Before'
                                        : 'After',
                              ),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ),
                    ],
                  );
                },
              ),
            if (items.length > 1)
              PositionedDirectional(
                end: 12,
                bottom: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: .58),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    context.l10n.isFa
                        ? '${toPersianDigits(_page + 1)} از ${toPersianDigits(items.length)}'
                        : '${_page + 1} of ${items.length}',
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _ServiceFacts extends StatelessWidget {
  const _ServiceFacts({required this.offer});

  final ServiceOffer offer;

  @override
  Widget build(BuildContext context) {
    final location =
        offer.location.isEmpty
            ? context.l10n.tr(fa: 'ثبت نشده', en: 'Not provided')
            : offer.location;
    final serviceArea =
        (offer.serviceArea ?? '').isEmpty ? location : offer.serviceArea!;

    return _SectionCard(
      icon: Icons.fact_check_outlined,
      title: context.l10n.tr(fa: 'مشخصات خدمت', en: 'Service information'),
      child: Column(
        children: [
          _FactRow(
            icon: Icons.category_outlined,
            label: context.l10n.tr(fa: 'دسته‌بندی', en: 'Category'),
            value:
                offer.category?.title ??
                context.l10n.tr(fa: 'ثبت نشده', en: 'Not provided'),
          ),
          const Divider(height: 22),
          _FactRow(
            icon: Icons.place_outlined,
            label: context.l10n.tr(fa: 'موقعیت', en: 'Location'),
            value: location,
          ),
          const Divider(height: 22),
          _FactRow(
            icon: Icons.map_outlined,
            label: context.l10n.tr(fa: 'محدوده خدمت', en: 'Service area'),
            value: serviceArea,
          ),
          const Divider(height: 22),
          _FactRow(
            icon: Icons.sell_outlined,
            label: context.l10n.tr(fa: 'نحوه محاسبه', en: 'Pricing'),
            value: servicePricingTypeLabel(context, offer.pricingType),
          ),
        ],
      ),
    );
  }
}

class _ProviderCard extends StatelessWidget {
  const _ProviderCard({required this.provider});

  final ServiceProviderSummary provider;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final avatarUrl = absoluteApiUrl(provider.avatarUrl);
    return _SectionCard(
      icon: Icons.storefront_outlined,
      title: context.l10n.tr(
        fa: 'اعتماد و عملکرد ارائه‌دهنده',
        en: 'Provider trust and performance',
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: colors.primaryContainer,
                backgroundImage:
                    avatarUrl == null ? null : NetworkImage(avatarUrl),
                child:
                    avatarUrl == null
                        ? Icon(
                          Icons.engineering_outlined,
                          color: colors.primary,
                        )
                        : null,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            serviceProviderName(context, provider),
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.w900),
                          ),
                        ),
                        if (provider.isVerified) ...[
                          const SizedBox(width: 5),
                          Icon(
                            Icons.verified_rounded,
                            size: 19,
                            color: colors.primary,
                          ),
                        ],
                      ],
                    ),
                    if ((provider.title ?? '').isNotEmpty) ...[
                      const SizedBox(height: 3),
                      Text(
                        provider.title!,
                        style: TextStyle(color: colors.onSurfaceVariant),
                      ),
                    ],
                    if (provider.location.isNotEmpty) ...[
                      const SizedBox(height: 3),
                      Text(
                        provider.location,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _MetricChip(
                icon: Icons.star_rounded,
                label: context.l10n.tr(
                  fa:
                      'امتیاز ${toPersianDigits(provider.ratingAverage.toStringAsFixed(1))}',
                  en: 'Rating ${provider.ratingAverage.toStringAsFixed(1)}',
                ),
              ),
              _MetricChip(
                icon: Icons.rate_review_outlined,
                label: context.l10n.tr(
                  fa: '${toPersianDigits(provider.reviewsCount)} نظر ثبت‌شده',
                  en: '${provider.reviewsCount} reviews',
                ),
              ),
              _MetricChip(
                icon: Icons.task_alt_rounded,
                label: context.l10n.tr(
                  fa:
                      '${toPersianDigits(provider.completedRequestsCount)} خدمت تکمیل‌شده',
                  en: '${provider.completedRequestsCount} completed services',
                ),
              ),
              if (provider.experienceYears != null)
                _MetricChip(
                  icon: Icons.workspace_premium_outlined,
                  label: context.l10n.tr(
                    fa: '${toPersianDigits(provider.experienceYears)} سال تجربه',
                    en: '${provider.experienceYears} years experience',
                  ),
                ),
              _MetricChip(
                icon:
                    provider.availabilityStatus == 'available'
                        ? Icons.bolt_rounded
                        : provider.availabilityStatus == 'busy'
                        ? Icons.schedule_rounded
                        : Icons.do_not_disturb_on_outlined,
                label: _availabilityLabel(context, provider),
              ),
              if (provider.typicalResponseMinutes != null)
                _MetricChip(
                  icon: Icons.quickreply_outlined,
                  label: _responseTimeLabel(
                    context,
                    provider.typicalResponseMinutes!,
                  ),
                ),
            ],
          ),
          if ((provider.bio ?? '').isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              provider.bio!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: colors.onSurfaceVariant,
                height: 1.65,
              ),
            ),
          ],
        ],
      ),
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
    final colors = Theme.of(context).colorScheme;
    return FarmGlassCard(
      borderRadius: 22,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: colors.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, size: 21, color: colors.primary),
              ),
              const SizedBox(width: 10),
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
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }
}

class _FactRow extends StatelessWidget {
  const _FactRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20, color: colors.onSurfaceVariant),
        const SizedBox(width: 9),
        SizedBox(
          width: 104,
          child: Text(label, style: TextStyle(color: colors.onSurfaceVariant)),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
      ],
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 17),
      label: Text(label),
      visualDensity: VisualDensity.compact,
    );
  }
}

String _availabilityLabel(
  BuildContext context,
  ServiceProviderSummary provider,
) {
  if (!provider.acceptingRequests ||
      provider.availabilityStatus == 'unavailable') {
    return context.l10n.tr(
      fa: 'موقتاً بدون پذیرش',
      en: 'Not accepting requests',
    );
  }
  if (provider.availabilityStatus == 'busy') {
    return context.l10n.tr(fa: 'پرمشغله', en: 'Busy');
  }
  return context.l10n.tr(fa: 'آماده پذیرش', en: 'Available');
}

String _responseTimeLabel(BuildContext context, int minutes) {
  if (minutes < 60) {
    return context.l10n.tr(
      fa: 'پاسخ معمولاً تا ${toPersianDigits(minutes)} دقیقه',
      en: 'Usually replies within $minutes min',
    );
  }
  final hours = (minutes / 60).ceil();
  return context.l10n.tr(
    fa: 'پاسخ معمولاً تا ${toPersianDigits(hours)} ساعت',
    en: 'Usually replies within $hours hr',
  );
}
