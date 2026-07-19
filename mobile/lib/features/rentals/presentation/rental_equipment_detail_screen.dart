import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/rental_models.dart';
import '../state/rental_discovery_controller.dart';

class RentalEquipmentDetailScreen extends ConsumerWidget {
  const RentalEquipmentDetailScreen({super.key, required this.equipmentId});
  final int equipmentId;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detail = ref.watch(rentalEquipmentDetailProvider(equipmentId));
    return Scaffold(
      appBar: const FarmAppBar(title: 'جزئیات تجهیز'),
      body: detail.when(
        loading: () => const FarmLoadingView(),
        error:
            (error, _) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('دریافت جزئیات تجهیز ناموفق بود.'),
                  TextButton(
                    onPressed:
                        () => ref.invalidate(
                          rentalEquipmentDetailProvider(equipmentId),
                        ),
                    child: const Text('تلاش دوباره'),
                  ),
                ],
              ),
            ),
        data: (data) => _Detail(data: data),
      ),
    );
  }
}

class _Detail extends StatelessWidget {
  const _Detail({required this.data});
  final RentalEquipmentDetail data;
  @override
  Widget build(BuildContext context) {
    final item = data.equipment;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (item.media.isEmpty)
          const SizedBox(
            height: 220,
            child: ColoredBox(
              color: Color(0xffeeeeee),
              child: Icon(Icons.agriculture, size: 72),
            ),
          )
        else
          SizedBox(
            height: 230,
            child: PageView(
              children:
                  item.media.map((media) {
                    final url = absoluteApiUrl(media.publicUrl);
                    return url == null
                        ? const Icon(Icons.image_not_supported_outlined)
                        : Image.network(
                          url,
                          fit: BoxFit.cover,
                          errorBuilder:
                              (_, _, _) =>
                                  const Icon(Icons.broken_image_outlined),
                        );
                  }).toList(),
            ),
          ),
        const SizedBox(height: 16),
        Text(item.title, style: Theme.of(context).textTheme.headlineSmall),
        if (item.category != null) Text(item.category!.title),
        if ((item.description ?? '').isNotEmpty) ...[
          const SizedBox(height: 12),
          Text(item.description!),
        ],
        const Divider(height: 32),
        _Info(label: 'موجر', value: item.lessorDisplayName ?? 'موجر تأییدشده'),
        _Info(
          label: 'حالت اپراتور',
          value: rentalOperatorLabel(item.operatorMode),
        ),
        if ((item.manufacturer ?? '').isNotEmpty)
          _Info(label: 'سازنده', value: item.manufacturer!),
        if ((item.modelName ?? '').isNotEmpty)
          _Info(label: 'مدل', value: item.modelName!),
        if (item.productionYear != null)
          _Info(label: 'سال ساخت', value: '${item.productionYear}'),
        _Info(
          label: 'ارسال تجهیز',
          value: item.deliveryAvailable ? 'امکان‌پذیر' : 'ندارد',
        ),
        if ((item.deliveryTerms ?? '').isNotEmpty)
          _Info(label: 'شرایط ارسال', value: item.deliveryTerms!),
        if (item.securityDepositAmount != null)
          _Info(
            label: 'ودیعه',
            value:
                '${item.securityDepositAmount!.toStringAsFixed(0)} ${item.currency}',
          ),
        const Divider(height: 32),
        Text('تعرفه‌های اجاره', style: Theme.of(context).textTheme.titleLarge),
        if (data.pricing.isEmpty)
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text('تعرفه فعالی ثبت نشده است.'),
          )
        else
          ...data.pricing.map(
            (price) => ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.payments_outlined),
              title: Text(
                '${price.priceAmount.toStringAsFixed(0)} ${price.currency} / ${rentalUnitLabel(price.unit)}',
              ),
              subtitle: Text(
                'حداقل ${price.minimumUnits} واحد${price.operatorIncluded ? '، همراه اپراتور' : ''}',
              ),
            ),
          ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed:
              () => context.push('/rentals/equipment/${item.id}/request'),
          icon: const Icon(Icons.calendar_month_outlined),
          label: const Text('درخواست اجاره'),
        ),
      ],
    );
  }
}

class _Info extends StatelessWidget {
  const _Info({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 5),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(width: 110, child: Text(label)),
        Expanded(child: Text(value)),
      ],
    ),
  );
}
