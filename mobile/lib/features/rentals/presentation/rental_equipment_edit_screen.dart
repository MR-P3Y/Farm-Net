import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/rental_models.dart';
import '../state/rental_management_controller.dart';

class RentalEquipmentEditScreen extends ConsumerStatefulWidget {
  const RentalEquipmentEditScreen({super.key, this.equipment});
  final RentalEquipmentOwner? equipment;
  @override
  ConsumerState<RentalEquipmentEditScreen> createState() => _State();
}

class _State extends ConsumerState<RentalEquipmentEditScreen> {
  final _title = TextEditingController(),
      _slug = TextEditingController(),
      _description = TextEditingController(),
      _manufacturer = TextEditingController(),
      _model = TextEditingController(),
      _year = TextEditingController(),
      _province = TextEditingController(),
      _city = TextEditingController(),
      _address = TextEditingController(),
      _deliveryTerms = TextEditingController(),
      _deposit = TextEditingController();
  final List<int> _media = [];
  int? _category;
  String _operator = 'without_operator';
  bool _delivery = false;
  @override
  void initState() {
    super.initState();
    final e = widget.equipment;
    if (e != null) {
      _title.text = e.title;
      _slug.text = e.slug;
      _description.text = e.description ?? '';
      _manufacturer.text = e.manufacturer ?? '';
      _model.text = e.modelName ?? '';
      _year.text = e.productionYear?.toString() ?? '';
      _province.text = e.provinceId?.toString() ?? '';
      _city.text = e.cityId?.toString() ?? '';
      _address.text = e.addressText ?? '';
      _deliveryTerms.text = e.deliveryTerms ?? '';
      _deposit.text = e.securityDepositAmount?.toString() ?? '';
      _category = e.categoryId;
      _operator = e.operatorMode;
      _delivery = e.deliveryAvailable;
      _media.addAll(e.media.map((m) => m.mediaFileId).whereType<int>());
    }
    Future.microtask(
      () => ref.read(rentalManagementProvider.notifier).loadEquipment(),
    );
  }

  @override
  void dispose() {
    for (final c in [
      _title,
      _slug,
      _description,
      _manufacturer,
      _model,
      _year,
      _province,
      _city,
      _address,
      _deliveryTerms,
      _deposit,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(rentalManagementProvider);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.equipment == null ? 'ثبت تجهیز' : 'ویرایش تجهیز'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (s.errorMessage != null)
            Text(
              s.errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          DropdownButtonFormField<int>(
            initialValue: _category,
            decoration: const InputDecoration(labelText: 'دسته‌بندی'),
            items:
                s.categories
                    .map(
                      (c) =>
                          DropdownMenuItem(value: c.id, child: Text(c.title)),
                    )
                    .toList(),
            onChanged: (v) => setState(() => _category = v),
          ),
          _f(_title, 'عنوان'),
          _f(_slug, 'نامک انگلیسی'),
          _f(_description, 'توضیحات', lines: 4),
          _f(_manufacturer, 'سازنده'),
          _f(_model, 'مدل'),
          _f(_year, 'سال ساخت', number: true),
          DropdownButtonFormField<String>(
            initialValue: _operator,
            decoration: const InputDecoration(labelText: 'حالت اپراتور'),
            items: const [
              DropdownMenuItem(
                value: 'without_operator',
                child: Text('بدون اپراتور'),
              ),
              DropdownMenuItem(
                value: 'with_operator',
                child: Text('همراه اپراتور'),
              ),
              DropdownMenuItem(value: 'either', child: Text('هر دو حالت')),
            ],
            onChanged: (v) => setState(() => _operator = v ?? _operator),
          ),
          _f(_province, 'شناسه استان', number: true),
          _f(_city, 'شناسه شهر', number: true),
          _f(_address, 'نشانی', lines: 2),
          SwitchListTile(
            value: _delivery,
            onChanged: (v) => setState(() => _delivery = v),
            title: const Text('امکان ارسال تجهیز'),
          ),
          _f(_deliveryTerms, 'شرایط ارسال', lines: 2),
          _f(_deposit, 'ودیعه', number: true),
          MediaUploadButton(
            label: 'افزودن تصویر تجهیز',
            purpose: 'general',
            visibility: 'public',
            allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
            onUploaded: (m) => setState(() => _media.add(m.id)),
          ),
          Text('${_media.length} تصویر انتخاب شده'),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: s.isSaving ? _null : _save,
            icon: const Icon(Icons.save_outlined),
            label: const Text('ذخیره تجهیز'),
          ),
        ],
      ),
    );
  }

  VoidCallback? get _null => null;
  Widget _f(
    TextEditingController c,
    String l, {
    int lines = 1,
    bool number = false,
  }) => Padding(
    padding: const EdgeInsets.only(top: 12),
    child: TextField(
      controller: c,
      minLines: lines,
      maxLines: lines,
      keyboardType: number ? TextInputType.number : null,
      decoration: InputDecoration(
        labelText: l,
        border: const OutlineInputBorder(),
      ),
    ),
  );
  Future<void> _save() async {
    if (_title.text.trim().length < 2 || _slug.text.trim().length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('عنوان و نامک را کامل کنید.')),
      );
      return;
    }
    final row = await ref
        .read(rentalManagementProvider.notifier)
        .saveEquipment(
          RentalEquipmentInput(
            title: _title.text.trim(),
            slug: _slug.text.trim(),
            operatorMode: _operator,
            mediaFileIds: _media,
            categoryId: _category,
            description: _description.text.trim(),
            manufacturer: _manufacturer.text.trim(),
            modelName: _model.text.trim(),
            productionYear: int.tryParse(_year.text),
            provinceId: int.tryParse(_province.text),
            cityId: int.tryParse(_city.text),
            addressText: _address.text.trim(),
            deliveryAvailable: _delivery,
            deliveryTerms: _deliveryTerms.text.trim(),
            securityDepositAmount: double.tryParse(_deposit.text),
          ),
          id: widget.equipment?.id,
        );
    if (row != null && mounted) context.go('/rentals/me/equipment');
  }
}
