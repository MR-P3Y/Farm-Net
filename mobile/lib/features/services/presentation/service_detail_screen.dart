import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../reviews/presentation/public_reviews_section.dart';
import '../data/service_models.dart';
import '../state/service_discovery_controller.dart';

class ServiceDetailScreen extends ConsumerWidget {
  const ServiceDetailScreen({required this.offerId, super.key});
  final int offerId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(serviceOfferDetailProvider(offerId));
    return Scaffold(
      appBar: AppBar(title: const Text('جزئیات خدمت')),
      body: detail.when(
        loading: () => const FarmLoadingView(),
        error:
            (_, __) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('دریافت جزئیات خدمت ناموفق بود.'),
                  TextButton.icon(
                    onPressed:
                        () =>
                            ref.invalidate(serviceOfferDetailProvider(offerId)),
                    icon: const Icon(Icons.refresh),
                    label: const Text('تلاش دوباره'),
                  ),
                ],
              ),
            ),
        data:
            (offer) => ResponsiveBuilder(
              builder:
                  (context, constraints, r) => SingleChildScrollView(
                    padding: r.pagePadding(),
                    child: Center(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 760),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            _Gallery(media: offer.media),
                            SizedBox(height: r.v(16)),
                            Text(
                              offer.title,
                              style: Theme.of(context).textTheme.headlineSmall,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _priceLabel(offer),
                              style: Theme.of(
                                context,
                              ).textTheme.titleMedium?.copyWith(
                                color: Theme.of(context).colorScheme.primary,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            if ((offer.shortDescription ?? '').isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Text(offer.shortDescription!),
                            ],
                            const Divider(height: 32),
                            _Info(
                              label: 'دسته‌بندی',
                              value: offer.category?.title ?? '-',
                            ),
                            _Info(
                              label: 'محدوده خدمت',
                              value:
                                  offer.serviceArea ??
                                  (offer.location.isEmpty
                                      ? '-'
                                      : offer.location),
                            ),
                            if ((offer.description ?? '').isNotEmpty) ...[
                              const Divider(height: 32),
                              Text(
                                'توضیحات',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              const SizedBox(height: 8),
                              Text(offer.description!),
                            ],
                            if (offer.provider != null) ...[
                              const Divider(height: 32),
                              _ProviderCard(provider: offer.provider!),
                            ],
                            const SizedBox(height: 12),
                            PublicReviewsSection(
                              subjectType: 'service_offer',
                              subjectId: offer.id,
                            ),
                            const SizedBox(height: 20),
                            FilledButton.icon(
                              onPressed:
                                  () => context.push(
                                    '/services/${offer.id}/request',
                                  ),
                              icon: const Icon(Icons.assignment_add),
                              label: const Text('ثبت درخواست این خدمت'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
            ),
      ),
    );
  }
}

class _Gallery extends StatelessWidget {
  const _Gallery({required this.media});
  final List<ServiceMedia> media;
  @override
  Widget build(BuildContext context) {
    if (media.isEmpty) {
      return const AspectRatio(
        aspectRatio: 16 / 9,
        child: ColoredBox(
          color: Color(0xFFE8F1E8),
          child: Icon(Icons.agriculture_outlined, size: 72),
        ),
      );
    }
    return SizedBox(
      height: 260,
      child: PageView(
        children:
            media.map((item) {
              final url = absoluteApiUrl(item.displayUrl);
              return ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child:
                    url == null
                        ? const Icon(Icons.image_outlined, size: 72)
                        : Image.network(
                          url,
                          fit: BoxFit.cover,
                          semanticLabel: item.altText,
                          errorBuilder:
                              (_, __, ___) => const Icon(
                                Icons.broken_image_outlined,
                                size: 72,
                              ),
                        ),
              );
            }).toList(),
      ),
    );
  }
}

class _ProviderCard extends StatelessWidget {
  const _ProviderCard({required this.provider});
  final ServiceProviderSummary provider;
  @override
  Widget build(BuildContext context) {
    final avatarUrl = absoluteApiUrl(provider.avatarUrl);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              backgroundImage:
                  avatarUrl == null ? null : NetworkImage(avatarUrl),
              child:
                  avatarUrl == null ? const Icon(Icons.person_outline) : null,
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
                          provider.resolvedName,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      if (provider.isVerified)
                        const Padding(
                          padding: EdgeInsets.only(right: 6),
                          child: Icon(Icons.verified, size: 18),
                        ),
                    ],
                  ),
                  if ((provider.title ?? '').isNotEmpty) Text(provider.title!),
                  if (provider.location.isNotEmpty) Text(provider.location),
                  if ((provider.bio ?? '').isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(provider.bio!),
                  ],
                  Text('${provider.completedRequestsCount} خدمت تکمیل‌شده'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Info extends StatelessWidget {
  const _Info({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Row(
      children: [
        SizedBox(width: 120, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}

String _priceLabel(ServiceOffer offer) {
  if (offer.pricingType == 'negotiable' || offer.priceAmount == null) {
    return 'قیمت توافقی';
  }
  return '${offer.priceAmount!.toStringAsFixed(0)} ${offer.currency == 'TOMAN' ? 'تومان' : offer.currency}';
}
