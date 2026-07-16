import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

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
      appBar: AppBar(
        title: Text(widget.offer == null ? 'خدمت جدید' : 'ویرایش خدمت'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (s.errorMessage != null)
            Text(
              s.errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          _f(_title, 'عنوان'),
          const SizedBox(height: 12),
          _f(_slug, 'نامک انگلیسی (مثال: soil-test)'),
          const SizedBox(height: 12),
          DropdownButtonFormField<int?>(
            initialValue: _categoryId,
            decoration: const InputDecoration(
              labelText: 'دسته‌بندی',
              border: OutlineInputBorder(),
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
          _f(_short, 'توضیح کوتاه'),
          const SizedBox(height: 12),
          _f(_description, 'توضیحات کامل', lines: 5),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _pricing,
            decoration: const InputDecoration(
              labelText: 'روش قیمت‌گذاری',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'fixed', child: Text('ثابت')),
              DropdownMenuItem(value: 'hourly', child: Text('ساعتی')),
              DropdownMenuItem(value: 'daily', child: Text('روزانه')),
              DropdownMenuItem(value: 'hectare', child: Text('هکتاری')),
              DropdownMenuItem(value: 'project', child: Text('پروژه‌ای')),
              DropdownMenuItem(value: 'negotiable', child: Text('توافقی')),
            ],
            onChanged: (v) => setState(() => _pricing = v ?? 'negotiable'),
          ),
          if (_pricing != 'negotiable') ...[
            const SizedBox(height: 12),
            _f(_price, 'قیمت (تومان)', number: true),
          ],
          const SizedBox(height: 12),
          _f(_province, 'استان'),
          const SizedBox(height: 12),
          _f(_city, 'شهر'),
          const SizedBox(height: 12),
          _f(_area, 'محدوده خدمت'),
          const SizedBox(height: 12),
          MediaUploadButton(
            label: 'افزودن تصویر خدمت',
            purpose: 'general',
            visibility: 'public',
            allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
            onUploaded: (m) => setState(() => _mediaIds.add(m.id)),
          ),
          if (_mediaIds.isNotEmpty)
            Text('${_mediaIds.length} تصویر انتخاب شده'),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: s.isSaving ? null : _save,
            icon: const Icon(Icons.save_outlined),
            label: const Text('ذخیره پیش‌نویس'),
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
        const SnackBar(content: Text('عنوان و نامک را کامل کنید.')),
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
          ),
          offerId: widget.offer?.id,
        );
    if (result != null && mounted) context.pop();
  }
}
