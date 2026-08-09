import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/service_models.dart';
import '../state/service_management_controller.dart';
import 'service_ui.dart';

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
  final _responseMinutes = TextEditingController();
  final Set<int> _categories = {};
  int? _avatarMediaId;
  bool _acceptingRequests = true;
  String _availabilityStatus = 'available';
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
      _responseMinutes,
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
    _acceptingRequests = p.acceptingRequests;
    _availabilityStatus = p.availabilityStatus;
    _responseMinutes.text = p.typicalResponseMinutes?.toString() ?? '';
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(serviceManagementProvider);
    _fill(state.profile);
    final p = state.profile;
    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(
          fa: 'پروفایل خدمات‌دهنده من',
          en: 'My service provider profile',
        ),
        fallbackLocation: '/activity',
      ),
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
                      title: Text(serviceOfferStatusLabel(context, p.status)),
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
                  _field(
                    _name,
                    context.l10n.tr(fa: 'نام نمایشی', en: 'Display name'),
                  ),
                  _field(
                    _title,
                    context.l10n.tr(
                      fa: 'عنوان حرفه‌ای',
                      en: 'Professional title',
                    ),
                  ),
                  _field(
                    _bio,
                    context.l10n.tr(
                      fa: 'معرفی و تجربه',
                      en: 'Bio and experience',
                    ),
                    lines: 4,
                  ),
                  _field(
                    _experience,
                    context.l10n.tr(fa: 'سال تجربه', en: 'Years of experience'),
                    number: true,
                  ),
                  _field(_phone, context.l10n.tr(fa: 'تلفن', en: 'Phone')),
                  _field(_email, context.l10n.tr(fa: 'ایمیل', en: 'Email')),
                  _field(
                    _province,
                    context.l10n.tr(fa: 'استان', en: 'Province'),
                  ),
                  _field(_city, context.l10n.tr(fa: 'شهر', en: 'City')),
                  _field(
                    _area,
                    context.l10n.tr(fa: 'محدوده خدمت', en: 'Service area'),
                  ),
                ].expand((w) => [w, const SizedBox(height: 12)]),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  value: _acceptingRequests,
                  onChanged:
                      (value) => setState(() => _acceptingRequests = value),
                  title: Text(
                    context.l10n.tr(
                      fa: 'در حال پذیرش درخواست جدید',
                      en: 'Accepting new requests',
                    ),
                  ),
                  subtitle: Text(
                    context.l10n.tr(
                      fa: 'در صورت غیرفعال‌بودن، دکمه ثبت درخواست بسته می‌شود.',
                      en: 'When disabled, customers cannot submit a request.',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _availabilityStatus,
                  decoration: InputDecoration(
                    labelText: context.l10n.tr(
                      fa: 'وضعیت دسترس‌پذیری',
                      en: 'Availability status',
                    ),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: 'available',
                      child: Text(
                        context.l10n.tr(fa: 'آماده خدمت', en: 'Available'),
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'busy',
                      child: Text(context.l10n.tr(fa: 'پرمشغله', en: 'Busy')),
                    ),
                    DropdownMenuItem(
                      value: 'unavailable',
                      child: Text(
                        context.l10n.tr(
                          fa: 'موقتاً در دسترس نیست',
                          en: 'Temporarily unavailable',
                        ),
                      ),
                    ),
                  ],
                  onChanged:
                      (value) => setState(
                        () => _availabilityStatus = value ?? 'available',
                      ),
                ),
                const SizedBox(height: 12),
                _field(
                  _responseMinutes,
                  context.l10n.tr(
                    fa: 'زمان پاسخ معمول (دقیقه)',
                    en: 'Typical response time (minutes)',
                  ),
                  number: true,
                ),
                const SizedBox(height: 12),
                Text(
                  context.l10n.tr(
                    fa: 'دسته‌های خدمات',
                    en: 'Service categories',
                  ),
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
                  label: context.l10n.tr(
                    fa: 'بارگذاری تصویر پروفایل',
                    en: 'Upload profile image',
                  ),
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
                  label: Text(
                    context.l10n.tr(fa: 'ذخیره پروفایل', en: 'Save profile'),
                  ),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed:
                      state.isSaving || p?.canSubmit != true ? null : _submit,
                  icon: const Icon(Icons.send_outlined),
                  label: Text(
                    context.l10n.tr(
                      fa: 'ارسال برای بررسی',
                      en: 'Submit for review',
                    ),
                  ),
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
            acceptingRequests: _acceptingRequests,
            availabilityStatus: _availabilityStatus,
            typicalResponseMinutes: int.tryParse(_responseMinutes.text),
          ),
        );
  }

  Future<void> _submit() async {
    final yes = await showDialog<bool>(
      context: context,
      builder:
          (c) => AlertDialog(
            title: Text(
              context.l10n.tr(fa: 'ارسال برای بررسی', en: 'Submit for review'),
            ),
            content: Text(
              context.l10n.tr(
                fa: 'پروفایل برای بررسی مدیر ارسال شود؟',
                en: 'Submit the profile for admin review?',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(c, false),
                child: Text(context.l10n.tr(fa: 'انصراف', en: 'Cancel')),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(c, true),
                child: Text(context.l10n.tr(fa: 'ارسال', en: 'Submit')),
              ),
            ],
          ),
    );
    if (yes == true) {
      await ref.read(serviceManagementProvider.notifier).submitProfile();
    }
  }
}
