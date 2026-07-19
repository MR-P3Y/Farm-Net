import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/rental_models.dart';
import '../state/rental_management_controller.dart';

class MyLessorProfileScreen extends ConsumerStatefulWidget {
  const MyLessorProfileScreen({super.key});
  @override
  ConsumerState<MyLessorProfileScreen> createState() => _State();
}

class _State extends ConsumerState<MyLessorProfileScreen> {
  final _name = TextEditingController(),
      _bio = TextEditingController(),
      _phone = TextEditingController(),
      _province = TextEditingController(),
      _city = TextEditingController(),
      _address = TextEditingController();
  int? _avatar;
  bool _filled = false;
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(rentalManagementProvider.notifier).loadProfile(),
    );
  }

  @override
  void dispose() {
    for (final c in [_name, _bio, _phone, _province, _city, _address]) {
      c.dispose();
    }
    super.dispose();
  }

  void _fill(LessorProfile? p) {
    if (_filled || p == null) return;
    _filled = true;
    _name.text = p.displayName ?? '';
    _bio.text = p.bio ?? '';
    _phone.text = p.phone ?? '';
    _province.text = p.provinceId?.toString() ?? '';
    _city.text = p.cityId?.toString() ?? '';
    _address.text = p.addressText ?? '';
    _avatar = p.avatarMediaFileId;
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(rentalManagementProvider);
    _fill(s.profile);
    final p = s.profile;
    return Scaffold(
      appBar: AppBar(title: const Text('پروفایل موجر من')),
      body:
          s.isLoading
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (p != null)
                    Card(
                      child: ListTile(
                        leading: const Icon(Icons.badge_outlined),
                        title: Text(rentalStatusLabel(p.status)),
                        subtitle:
                            (p.adminNote ?? '').isEmpty
                                ? Text('${p.equipmentCount} تجهیز')
                                : Text(p.adminNote!),
                      ),
                    ),
                  if (s.errorMessage != null)
                    Text(
                      s.errorMessage!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  if (s.successMessage != null) Text(s.successMessage!),
                  _field(_name, 'نام نمایشی'),
                  _field(_bio, 'معرفی موجر', lines: 4),
                  _field(_phone, 'تلفن'),
                  _field(_province, 'شناسه استان', number: true),
                  _field(_city, 'شناسه شهر', number: true),
                  _field(_address, 'نشانی', lines: 3),
                  MediaUploadButton(
                    label: 'بارگذاری تصویر موجر',
                    purpose: 'general',
                    visibility: 'public',
                    allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
                    onUploaded: (m) => setState(() => _avatar = m.id),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: s.isSaving || p?.canEdit == false ? null : _save,
                    icon: const Icon(Icons.save_outlined),
                    label: const Text('ذخیره پروفایل'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed:
                        s.isSaving || p?.canSubmit != true
                            ? null
                            : () =>
                                ref
                                    .read(rentalManagementProvider.notifier)
                                    .submitProfile(),
                    icon: const Icon(Icons.send_outlined),
                    label: const Text('ارسال برای بررسی'),
                  ),
                ],
              ),
    );
  }

  Widget _field(
    TextEditingController c,
    String label, {
    int lines = 1,
    bool number = false,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: TextField(
      controller: c,
      minLines: lines,
      maxLines: lines,
      keyboardType: number ? TextInputType.number : null,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
    ),
  );
  void _save() => ref
      .read(rentalManagementProvider.notifier)
      .saveProfile(
        LessorProfileInput(
          displayName: _name.text.trim(),
          bio: _bio.text.trim(),
          phone: _phone.text.trim(),
          provinceId: int.tryParse(_province.text),
          cityId: int.tryParse(_city.text),
          addressText: _address.text.trim(),
          avatarMediaFileId: _avatar,
        ),
      );
}

String rentalStatusLabel(String s) =>
    const {
      'draft': 'پیش‌نویس',
      'pending_review': 'در انتظار بررسی',
      'approved': 'تأییدشده',
      'rejected': 'ردشده',
      'suspended': 'تعلیق‌شده',
      'archived': 'بایگانی‌شده',
    }[s] ??
    s;
