import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';
import '../domain/farm_profile_input.dart';

class FarmProfileEditorScreen extends ConsumerStatefulWidget {
  const FarmProfileEditorScreen({this.farm, super.key});

  final FarmModel? farm;

  bool get isEditing => farm != null;

  @override
  ConsumerState<FarmProfileEditorScreen> createState() =>
      _FarmProfileEditorScreenState();
}

class _FarmProfileEditorScreenState
    extends ConsumerState<FarmProfileEditorScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _name;
  late final TextEditingController _description;
  late final TextEditingController _area;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _name = TextEditingController(text: widget.farm?.name ?? '');
    _description = TextEditingController(text: widget.farm?.description ?? '');
    _area = TextEditingController(
      text: formatFarmAreaInput(widget.farm?.declaredAreaSqm),
    );
  }

  @override
  void dispose() {
    _name.dispose();
    _description.dispose();
    _area.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_saving || !_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    final description = _description.text.trim();
    final payload = <String, dynamic>{
      'name': _name.text.trim(),
      'description': description.isEmpty ? null : description,
      'declared_area_sqm': parseFarmArea(_area.text),
    };
    try {
      final repository = ref.read(farmRepositoryProvider);
      final result =
          widget.farm == null
              ? await repository.createFarm(payload)
              : await repository.updateFarm(widget.farm!.id, payload);
      if (mounted) Navigator.of(context).pop(result);
    } catch (error) {
      if (!mounted) return;
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'ذخیره پروفایل مزرعه انجام نشد: $error',
              en: 'Could not save the farm profile: $error',
            ),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return PopScope(
      canPop: !_saving,
      child: Scaffold(
        appBar: FarmAppBar(
          title: l10n.tr(
            fa: widget.isEditing ? 'ویرایش مزرعه' : 'ثبت مزرعه جدید',
            en: widget.isEditing ? 'Edit farm' : 'Add farm',
          ),
        ),
        body: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 112),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const CircleAvatar(
                        child: Icon(Icons.agriculture_rounded),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              l10n.tr(fa: 'پروفایل مزرعه', en: 'Farm profile'),
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              l10n.tr(
                                fa:
                                    'فعلاً فقط نام الزامی است؛ توضیحات و مساحت را هر زمان می‌توانید تکمیل کنید.',
                                en:
                                    'Only the name is required. Description and area can be completed later.',
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _name,
                enabled: !_saving,
                autofocus: !widget.isEditing,
                textInputAction: TextInputAction.next,
                maxLength: 180,
                decoration: InputDecoration(
                  labelText: l10n.tr(fa: 'نام مزرعه *', en: 'Farm name *'),
                  prefixIcon: const Icon(Icons.badge_outlined),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return l10n.tr(
                      fa: 'نام مزرعه را وارد کنید',
                      en: 'Enter the farm name',
                    );
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _area,
                enabled: !_saving,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: l10n.tr(
                    fa: 'مساحت کل (متر مربع)',
                    en: 'Total area (m²)',
                  ),
                  prefixIcon: const Icon(Icons.square_foot_rounded),
                  helperText: l10n.tr(
                    fa: 'اختیاری؛ نباید از مجموع مساحت قطعات کمتر باشد.',
                    en: 'Optional; cannot be less than the total Plot area.',
                  ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) return null;
                  final area = parseFarmArea(value);
                  if (area == null || !area.isFinite || area <= 0) {
                    return l10n.tr(
                      fa: 'یک مساحت معتبر و بزرگ‌تر از صفر وارد کنید',
                      en: 'Enter a valid area greater than zero',
                    );
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _description,
                enabled: !_saving,
                minLines: 3,
                maxLines: 6,
                maxLength: 5000,
                textInputAction: TextInputAction.newline,
                decoration: InputDecoration(
                  labelText: l10n.tr(
                    fa: 'توضیحات (اختیاری)',
                    en: 'Description (optional)',
                  ),
                  alignLabelWithHint: true,
                  prefixIcon: const Padding(
                    padding: EdgeInsets.only(bottom: 72),
                    child: Icon(Icons.notes_rounded),
                  ),
                ),
              ),
            ],
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: FilledButton.icon(
              onPressed: _saving ? null : _save,
              icon:
                  _saving
                      ? const SizedBox.square(
                        dimension: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : const Icon(Icons.check_rounded),
              label: Text(
                _saving
                    ? l10n.tr(fa: 'در حال ذخیره...', en: 'Saving...')
                    : l10n.tr(
                      fa: widget.isEditing ? 'ذخیره تغییرات' : 'ثبت مزرعه',
                      en: widget.isEditing ? 'Save changes' : 'Create farm',
                    ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
