import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/service_models.dart';
import '../state/service_management_controller.dart';

class OfferEditScreen extends ConsumerStatefulWidget {
  const OfferEditScreen({this.offer, super.key});
  final ServiceOfferOwner? offer;
  @override
  ConsumerState<OfferEditScreen> createState() => _State();
}

class _State extends ConsumerState<OfferEditScreen> {
  final _title = TextEditingController(),
      _slug = TextEditingController(),
      _short = TextEditingController(),
      _description = TextEditingController(),
      _price = TextEditingController(),
      _province = TextEditingController(),
      _city = TextEditingController(),
      _area = TextEditingController();
  int? _categoryId;
  String _pricing = 'negotiable';
  final List<int> _mediaIds = [];
  final Map<int, String?> _mediaStages = {};
  bool _loaded = false;
  @override
  void initState() {
    super.initState();
    final o = widget.offer;
    if (o != null) {
      _title.text = o.title;
      _slug.text = o.slug ?? '';
      _short.text = o.shortDescription ?? '';
      _description.text = o.description ?? '';
      _price.text = o.priceAmount?.toString() ?? '';
      _province.text = o.provinceName ?? '';
      _city.text = o.cityName ?? '';
      _area.text = o.serviceArea ?? '';
      _categoryId = o.categoryId;
      _pricing = o.pricingType;
      _mediaIds.addAll(o.media.map((m) => m.mediaFileId).whereType<int>());
      for (final media in o.media) {
        if (media.mediaFileId != null) {
          _mediaStages[media.mediaFileId!] = media.portfolioStage;
        }
      }
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    if (ref.read(serviceManagementProvider).categories.isEmpty) {
      Future.microtask(
        () => ref.read(serviceManagementProvider.notifier).loadOffers(),
      );
    }
  }

  @override
  void dispose() {
    for (final c in [
      _title,
      _slug,
      _short,
      _description,
      _price,
      _province,
      _city,
      _area,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(serviceManagementProvider);
    return Scaffold(
      appBar: FarmAppBar(
        title:
            widget.offer == null
                ? context.l10n.tr(fa: 'خدمت جدید', en: 'New service')
                : context.l10n.tr(fa: 'ویرایش خدمت', en: 'Edit service'),
        fallbackLocation: '/services/me/offers',
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (s.errorMessage != null)
            Text(
              s.errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          _f(_title, context.l10n.tr(fa: 'عنوان', en: 'Title')),
          const SizedBox(height: 12),
          _f(
            _slug,
            context.l10n.tr(
              fa: 'نامک انگلیسی (مثال: soil-test)',
              en: 'English slug (example: soil-test)',
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<int?>(
            initialValue: _categoryId,
            decoration: InputDecoration(
              labelText: context.l10n.tr(fa: 'دسته‌بندی', en: 'Category'),
            ),
            items:
                s.categories
                    .map(
                      (c) =>
                          DropdownMenuItem(value: c.id, child: Text(c.title)),
                    )
                    .toList(),
            onChanged: (v) => setState(() => _categoryId = v),
          ),
          const SizedBox(height: 12),
          _f(
            _short,
            context.l10n.tr(fa: 'توضیح کوتاه', en: 'Short description'),
          ),
          const SizedBox(height: 12),
          _f(
            _description,
            context.l10n.tr(fa: 'توضیحات کامل', en: 'Full description'),
            lines: 5,
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _pricing,
            decoration: InputDecoration(
              labelText: context.l10n.tr(
                fa: 'روش قیمت‌گذاری',
                en: 'Pricing method',
              ),
            ),
            items: [
              for (final type in const [
                'fixed',
                'hourly',
                'daily',
                'hectare',
                'project',
                'negotiable',
              ])
                DropdownMenuItem(
                  value: type,
                  child: Text(switch (type) {
                    'fixed' => context.l10n.tr(fa: 'ثابت', en: 'Fixed'),
                    'hourly' => context.l10n.tr(fa: 'ساعتی', en: 'Hourly'),
                    'daily' => context.l10n.tr(fa: 'روزانه', en: 'Daily'),
                    'hectare' => context.l10n.tr(
                      fa: 'هکتاری',
                      en: 'Per hectare',
                    ),
                    'project' => context.l10n.tr(
                      fa: 'پروژه‌ای',
                      en: 'Per project',
                    ),
                    _ => context.l10n.tr(fa: 'توافقی', en: 'Negotiable'),
                  }),
                ),
            ],
            onChanged: (v) => setState(() => _pricing = v ?? 'negotiable'),
          ),
          if (_pricing != 'negotiable') ...[
            const SizedBox(height: 12),
            _f(
              _price,
              context.l10n.tr(fa: 'قیمت (تومان)', en: 'Price (Toman)'),
              number: true,
            ),
          ],
          const SizedBox(height: 12),
          _f(_province, context.l10n.tr(fa: 'استان', en: 'Province')),
          const SizedBox(height: 12),
          _f(_city, context.l10n.tr(fa: 'شهر', en: 'City')),
          const SizedBox(height: 12),
          _f(_area, context.l10n.tr(fa: 'محدوده خدمت', en: 'Service area')),
          const SizedBox(height: 12),
          MediaUploadButton(
            label: context.l10n.tr(
              fa: 'افزودن تصویر خدمت',
              en: 'Add service image',
            ),
            purpose: 'general',
            visibility: 'public',
            allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
            onUploaded:
                (m) => setState(() {
                  _mediaIds.add(m.id);
                  _mediaStages[m.id] = null;
                }),
          ),
          if (_mediaIds.isNotEmpty)
            ..._mediaIds.map(
              (mediaId) => Card(
                child: ListTile(
                  leading: const Icon(Icons.photo_outlined),
                  title: Text(
                    context.l10n.tr(fa: 'تصویر $mediaId', en: 'Image $mediaId'),
                  ),
                  subtitle: DropdownButton<String?>(
                    value: _mediaStages[mediaId],
                    isExpanded: true,
                    hint: Text(
                      context.l10n.tr(
                        fa: 'نمونه‌کار عادی',
                        en: 'Regular portfolio image',
                      ),
                    ),
                    items: [
                      DropdownMenuItem(
                        value: null,
                        child: Text(context.l10n.tr(fa: 'عادی', en: 'Regular')),
                      ),
                      DropdownMenuItem(
                        value: 'before',
                        child: Text(context.l10n.tr(fa: 'قبل', en: 'Before')),
                      ),
                      DropdownMenuItem(
                        value: 'after',
                        child: Text(context.l10n.tr(fa: 'بعد', en: 'After')),
                      ),
                    ],
                    onChanged:
                        (value) =>
                            setState(() => _mediaStages[mediaId] = value),
                  ),
                  trailing: IconButton(
                    tooltip: context.l10n.tr(
                      fa: 'حذف تصویر',
                      en: 'Remove image',
                    ),
                    onPressed:
                        () => setState(() {
                          _mediaIds.remove(mediaId);
                          _mediaStages.remove(mediaId);
                        }),
                    icon: const Icon(Icons.delete_outline),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: s.isSaving ? null : _save,
            icon: const Icon(Icons.save_outlined),
            label: Text(
              context.l10n.tr(fa: 'ذخیره پیش‌نویس', en: 'Save draft'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _f(
    TextEditingController c,
    String l, {
    int lines = 1,
    bool number = false,
  }) => TextField(
    controller: c,
    minLines: lines,
    maxLines: lines,
    keyboardType: number ? TextInputType.number : null,
    decoration: InputDecoration(
      labelText: l,
      border: const OutlineInputBorder(),
    ),
  );
  Future<void> _save() async {
    if (_title.text.trim().length < 2 || _slug.text.trim().length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'عنوان و نامک را کامل کنید.',
              en: 'Complete the title and slug.',
            ),
          ),
        ),
      );
      return;
    }
    final result = await ref
        .read(serviceManagementProvider.notifier)
        .saveOffer(
          ServiceOfferInput(
            title: _title.text.trim(),
            slug: _slug.text.trim(),
            categoryId: _categoryId,
            shortDescription: _short.text.trim(),
            description: _description.text.trim(),
            pricingType: _pricing,
            priceAmount:
                _pricing == 'negotiable' ? null : double.tryParse(_price.text),
            provinceName: _province.text.trim(),
            cityName: _city.text.trim(),
            serviceArea: _area.text.trim(),
            mediaFileIds: _mediaIds,
            mediaStages: _mediaStages,
          ),
          offerId: widget.offer?.id,
        );
    if (result != null && mounted) {
      if (Navigator.canPop(context)) {
        context.pop();
      } else {
        context.go('/services/me/offers');
      }
    }
  }
}
