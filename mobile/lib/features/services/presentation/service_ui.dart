import 'package:flutter/material.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/money.dart';
import '../data/service_models.dart';

IconData serviceCategoryIcon(ServiceCategory? category) {
  return switch (category?.code) {
    'spraying' => Icons.water_drop_outlined,
    'plowing' => Icons.agriculture_outlined,
    'pruning' => Icons.content_cut_rounded,
    'harvesting' => Icons.grass_rounded,
    'crop_transport' => Icons.local_shipping_outlined,
    'soil_testing' => Icons.science_outlined,
    'irrigation_installation' => Icons.water_outlined,
    'labor' => Icons.groups_2_outlined,
    _ => _categoryTitleIcon(category?.title),
  };
}

IconData _categoryTitleIcon(String? title) {
  if (title == null) return Icons.grid_view_rounded;
  if (title.contains('سم')) return Icons.water_drop_outlined;
  if (title.contains('شخم')) return Icons.agriculture_outlined;
  if (title.contains('هرس')) return Icons.content_cut_rounded;
  if (title.contains('برداشت')) return Icons.grass_rounded;
  if (title.contains('حمل')) return Icons.local_shipping_outlined;
  if (title.contains('خاک')) return Icons.science_outlined;
  if (title.contains('آبیاری')) return Icons.water_outlined;
  if (title.contains('کارگر')) return Icons.groups_2_outlined;
  return Icons.handyman_outlined;
}

String servicePricingTypeLabel(BuildContext context, String type) {
  return switch (type) {
    'fixed' => context.l10n.tr(fa: 'قیمت ثابت', en: 'Fixed price'),
    'hourly' => context.l10n.tr(fa: 'ساعتی', en: 'Hourly'),
    'daily' => context.l10n.tr(fa: 'روزانه', en: 'Daily'),
    'hectare' => context.l10n.tr(fa: 'هکتاری', en: 'Per hectare'),
    'project' => context.l10n.tr(fa: 'پروژه‌ای', en: 'Per project'),
    'negotiable' => context.l10n.tr(fa: 'توافقی', en: 'Negotiable'),
    _ => type,
  };
}

String servicePriceLabel(BuildContext context, ServiceOffer offer) {
  if (offer.pricingType == 'negotiable' || offer.priceAmount == null) {
    return context.l10n.tr(fa: 'قیمت توافقی', en: 'Negotiable price');
  }

  final amount =
      offer.currency == 'TOMAN'
          ? formatToman(context, offer.priceAmount!)
          : '${offer.priceAmount!.toStringAsFixed(0)} ${offer.currency}';
  return '$amount • ${servicePricingTypeLabel(context, offer.pricingType)}';
}

String serviceRequestStatusLabel(BuildContext context, String status) {
  if (context.l10n.isFa) return requestStatusLabel(status);
  return switch (status) {
    'open' => 'Open',
    'accepted' => 'Accepted',
    'in_progress' => 'In progress',
    'completed' => 'Completed',
    'cancelled' => 'Cancelled',
    'rejected' => 'Rejected',
    _ => status,
  };
}

String serviceOfferStatusLabel(BuildContext context, String status) {
  if (context.l10n.isFa) return serviceStatusLabel(status);
  return switch (status) {
    'draft' => 'Draft',
    'pending_review' => 'Pending review',
    'approved' => 'Approved',
    'rejected' => 'Rejected',
    'suspended' => 'Suspended',
    'archived' => 'Archived',
    _ => status,
  };
}

String serviceContactMethodLabel(BuildContext context, String? method) =>
    switch (method) {
      'in_app' => context.l10n.tr(fa: 'داخل اپلیکیشن', en: 'In app'),
      'phone' => context.l10n.tr(fa: 'تماس تلفنی', en: 'Phone call'),
      'video' => context.l10n.tr(fa: 'تماس تصویری', en: 'Video call'),
      'visit' => context.l10n.tr(fa: 'بازدید حضوری', en: 'On-site visit'),
      _ => '-',
    };

String serviceProviderName(
  BuildContext context,
  ServiceProviderSummary? provider,
) {
  final displayName = provider?.displayName?.trim();
  if (displayName?.isNotEmpty == true) return displayName!;
  final name = provider?.name?.trim();
  if (name?.isNotEmpty == true) return name!;
  return context.l10n.tr(fa: 'خدمات‌دهنده', en: 'Service provider');
}
