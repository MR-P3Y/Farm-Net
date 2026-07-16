import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/service_models.dart';
import '../state/service_management_controller.dart';

class MyProviderProfileScreen extends ConsumerStatefulWidget {
  const MyProviderProfileScreen({super.key});
  @override
  ConsumerState<MyProviderProfileScreen> createState() => _State();
}

class _State extends ConsumerState<MyProviderProfileScreen> {
  final _name = TextEditingController();
  final _title = TextEditingController();
  final _bio = TextEditingController();
  final _experience = TextEditingController();
  final _phone = TextEditingController();
  final _email = TextEditingController();
  final _province = TextEditingController();
  final _city = TextEditingController();
  final _area = TextEditingController();
  final Set<int> _categories = {};
  int? _avatarMediaId;
  bool _loaded = false;
  bool _filled = false;
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loaded) return;
    _loaded = true;
    Future.microtask(
      () => ref.read(serviceManagementProvider.notifier).loadProfile(),
    );
  }

  @override
  void dispose() {
    for (final c in [
      _name,
      _title,
      _bio,
      _experience,
      _phone,
      _email,
      _province,
      _city,
      _area,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  void _fill(ServiceProviderProfileOwner? p) {
    if (_filled || p == null) return;
    _filled = true;
    _name.text = p.displayName ?? '';
    _title.text = p.title ?? '';
    _bio.text = p.bio ?? '';
    _experience.text = p.experienceYears?.toString() ?? '';
    _phone.text = p.phone ?? '';
    _email.text = p.email ?? '';
    _province.text = p.provinceName ?? '';
    _city.text = p.cityName ?? '';
    _area.text = p.serviceArea ?? '';
    _categories.addAll(p.categories.map((e) => e.id));
    _avatarMediaId = p.avatarMediaFileId;
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceManagementProvider);
    _fill(state.profile);
    final p = state.profile;
    return Scaffold(
      appBar: AppBar(title: const Text('پروفایل خدمات‌دهنده من')),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return RefreshIndicator(
            onRefresh:
                () =>
                    ref.read(serviceManagementProvider.notifier).loadProfile(),
            child: ListView(
              padding: r.pagePadding(),
              children: [
                if (p != null)
                  Card(
                    child: ListTile(
                      title: Text(p.statusLabelFa),
                      leading: const Icon(Icons.badge_outlined),
                      subtitle:
                          (p.adminNote ?? '').isEmpty
                              ? null
                              : Text(p.adminNote!),
                    ),
                  ),
                if (state.errorMessage != null)
                  Text(
                    state.errorMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                if (state.successMessage != null)
                  Text(
                    state.successMessage!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ...[
                  _field(_name, 'نام نمایشی'),
                  _field(_title, 'عنوان حرفه‌ای'),
                  _field(_bio, 'معرفی و تجربه', lines: 4),
                  _field(_experience, 'سال تجربه', number: true),
                  _field(_phone, 'تلفن'),
                  _field(_email, 'ایمیل'),
                  _field(_province, 'استان'),
                  _field(_city, 'شهر'),
                  _field(_area, 'محدوده خدمت'),
                ].expand((w) => [w, const SizedBox(height: 12)]),
                Text(
                  'دسته‌های خدمات',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Wrap(
                  spacing: 8,
                  children:
                      state.categories
                          .map(
                            (c) => FilterChip(
                              label: Text(c.title),
                              selected: _categories.contains(c.id),
                              onSelected:
                                  (v) => setState(
                                    () =>
                                        v
                                            ? _categories.add(c.id)
                                            : _categories.remove(c.id),
                                  ),
                            ),
                          )
                          .toList(),
                ),
                const SizedBox(height: 12),
                MediaUploadButton(
                  label: 'بارگذاری تصویر پروفایل',
                  purpose: 'general',
                  visibility: 'public',
                  allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
                  onUploaded: (m) => setState(() => _avatarMediaId = m.id),
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed:
                      state.isSaving || p?.canEdit == false ? null : _save,
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('ذخیره پروفایل'),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed:
                      state.isSaving || p?.canSubmit != true ? null : _submit,
                  icon: const Icon(Icons.send_outlined),
                  label: const Text('ارسال برای بررسی'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _field(
    TextEditingController c,
    String label, {
    int lines = 1,
    bool number = false,
  }) => TextField(
    controller: c,
    minLines: lines,
    maxLines: lines,
    keyboardType: number ? TextInputType.number : null,
    decoration: InputDecoration(
      labelText: label,
      border: const OutlineInputBorder(),
    ),
  );
  Future<void> _save() async {
    await ref
        .read(serviceManagementProvider.notifier)
        .saveProfile(
          ServiceProviderProfileInput(
            categoryIds: _categories.toList(),
            displayName: _name.text.trim(),
            title: _title.text.trim(),
            bio: _bio.text.trim(),
            experienceYears: int.tryParse(_experience.text),
            phone: _phone.text.trim(),
            email: _email.text.trim(),
            provinceName: _province.text.trim(),
            cityName: _city.text.trim(),
            serviceArea: _area.text.trim(),
            avatarMediaFileId: _avatarMediaId,
          ),
        );
  }

  Future<void> _submit() async {
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (c) => AlertDialog(
            title: const Text('ارسال برای بررسی'),
            content: const Text('پروفایل برای بررسی مدیر ارسال شود؟'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: const Text('انصراف'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: const Text('ارسال'),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref.read(serviceManagementProvider.notifier).submitProfile();
    }
  }
}
