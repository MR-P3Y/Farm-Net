import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/responsive/responsive.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_error_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_primary_action_bar.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../../geo/data/geo_models.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/profile_models.dart';
import '../state/profile_controller.dart';
import '../state/profile_state.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _displayNameController = TextEditingController();
  final _nationalIdController = TextEditingController();
  final _addressController = TextEditingController();
  final _postalCodeController = TextEditingController();
  final _bioController = TextEditingController();

  DateTime? _birthDate;
  String _gender = '';
  int? _provinceId;
  int? _countyId;
  int? _cityId;
  String? _avatarFileId;
  String? _avatarUrl;
  bool _filled = false;
  bool _requestedLoad = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_requestedLoad) return;
    _requestedLoad = true;
    if (ref.read(profileControllerProvider).profile == null) {
      Future.microtask(
        () => ref.read(profileControllerProvider.notifier).load(),
      );
    }
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _displayNameController.dispose();
    _nationalIdController.dispose();
    _addressController.dispose();
    _postalCodeController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  void _fillOnce(UserProfile? profile) {
    if (_filled || profile == null) return;
    _filled = true;

    _firstNameController.text = profile.firstName ?? '';
    _lastNameController.text = profile.lastName ?? '';
    _displayNameController.text = profile.displayName ?? '';
    _nationalIdController.text = profile.nationalId ?? '';
    _addressController.text = profile.address ?? '';
    _postalCodeController.text = profile.postalCode ?? '';
    _bioController.text = profile.bio ?? '';

    _birthDate = DateTime.tryParse(profile.birthDate ?? '');
    _gender = profile.gender ?? '';
    _provinceId = profile.provinceId;
    _countyId = profile.countyId;
    _cityId = profile.cityId;
    _avatarFileId = profile.avatarUrl == null ? null : profile.avatarFileId;
    _avatarUrl = profile.avatarUrl;
  }

  Future<void> _pickBirthDate() async {
    final now = DateTime.now();
    final selected = await showLocalizedDatePicker(
      context: context,
      initialDate: _birthDate ?? DateTime(now.year - 30, now.month, now.day),
      firstDate: DateTime(1900),
      lastDate: DateTime(now.year, now.month, now.day),
      helpText: context.l10n.tr(
        fa: 'انتخاب تاریخ تولد',
        en: 'Select date of birth',
      ),
    );
    if (selected == null || !mounted) return;
    setState(() => _birthDate = selected);
  }

  Future<void> _save() async {
    if (ref.read(profileControllerProvider).isSaving) return;
    if (_formKey.currentState?.validate() != true) return;
    FocusManager.instance.primaryFocus?.unfocus();

    final input = ProfileUpdateInput(
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      displayName: _displayNameController.text.trim(),
      nationalId: toEnglishDigits(_nationalIdController.text.trim()),
      birthDate: _birthDate?.toIso8601String().split('T').first,
      gender: _gender,
      provinceId: _provinceId,
      countyId: _countyId,
      cityId: _cityId,
      address: _addressController.text.trim(),
      postalCode: toEnglishDigits(_postalCodeController.text.trim()),
      avatarFileId: _avatarFileId,
      bio: _bioController.text.trim(),
    );

    final ok = await ref.read(profileControllerProvider.notifier).update(input);
    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileControllerProvider);
    final l10n = context.l10n;
    _fillOnce(state.profile);

    final selectedProvinceId =
        state.provinces.any((item) => item.id == _provinceId)
            ? _provinceId
            : null;
    final selectedCountyId =
        state.counties.any((item) => item.id == _countyId) ? _countyId : null;
    final selectedCityId =
        state.cities.any((item) => item.id == _cityId) ? _cityId : null;

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.tr(fa: 'ویرایش پروفایل', en: 'Edit profile'),
        fallbackLocation: '/profile',
      ),
      bottomNavigationBar:
          state.isLoading
              ? null
              : FarmPrimaryActionBar(
                label: l10n.tr(fa: 'ذخیره تغییرات', en: 'Save changes'),
                loadingLabel: l10n.tr(
                  fa: 'در حال ذخیره تغییرات…',
                  en: 'Saving changes…',
                ),
                icon: Icons.check_rounded,
                isLoading: state.isSaving,
                onPressed: _save,
              ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return FarmLoadingView(
              message: l10n.tr(
                fa: 'در حال دریافت اطلاعات پروفایل…',
                en: 'Loading your profile…',
              ),
            );
          }
          if (state.profile == null && state.errorMessage != null) {
            return FarmErrorView(
              message: l10n.tr(
                fa: 'دریافت اطلاعات پروفایل انجام نشد.',
                en: 'Could not load your profile.',
              ),
              onRetry:
                  () => ref.read(profileControllerProvider.notifier).load(),
            );
          }

          return Stack(
            children: [
              Positioned.fill(
                child: AbsorbPointer(
                  key: const Key('profile-saving-lock'),
                  absorbing: state.isSaving,
                  child: AnimatedOpacity(
                    duration: const Duration(milliseconds: 180),
                    opacity: state.isSaving ? .72 : 1,
                    child: Form(
                      key: _formKey,
                      child: SingleChildScrollView(
                        padding: r.pagePadding().copyWith(bottom: r.v(28)),
                        child: Center(
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 760),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _AvatarEditor(
                                  avatarUrl: _avatarUrl,
                                  onUploaded: (fileKey, publicUrl) {
                                    setState(() {
                                      _avatarFileId = fileKey;
                                      _avatarUrl = publicUrl;
                                    });
                                  },
                                  onClear:
                                      _avatarFileId == null &&
                                              _avatarUrl == null
                                          ? null
                                          : () => setState(() {
                                            _avatarFileId = null;
                                            _avatarUrl = null;
                                          }),
                                ),
                                SizedBox(height: r.v(14)),
                                _FormSection(
                                  title: l10n.tr(
                                    fa: 'اطلاعات هویتی',
                                    en: 'Personal information',
                                  ),
                                  icon: Icons.badge_outlined,
                                  children: [
                                    FarmTextField(
                                      controller: _firstNameController,
                                      label: l10n.tr(
                                        fa: 'نام',
                                        en: 'First name',
                                      ),
                                      validator:
                                          (value) => _required(
                                            value,
                                            l10n.tr(
                                              fa: 'نام',
                                              en: 'First name',
                                            ),
                                          ),
                                    ),
                                    FarmTextField(
                                      controller: _lastNameController,
                                      label: l10n.tr(
                                        fa: 'نام خانوادگی',
                                        en: 'Last name',
                                      ),
                                      validator:
                                          (value) => _required(
                                            value,
                                            l10n.tr(
                                              fa: 'نام خانوادگی',
                                              en: 'Last name',
                                            ),
                                          ),
                                    ),
                                    FarmTextField(
                                      controller: _displayNameController,
                                      label: l10n.tr(
                                        fa: 'نام نمایشی',
                                        en: 'Display name',
                                      ),
                                    ),
                                    FarmTextField(
                                      controller: _nationalIdController,
                                      label: l10n.tr(
                                        fa: 'کد ملی',
                                        en: 'National ID',
                                      ),
                                      keyboardType: TextInputType.number,
                                      validator: _validateNationalId,
                                    ),
                                    InkWell(
                                      borderRadius: BorderRadius.circular(14),
                                      onTap: _pickBirthDate,
                                      child: InputDecorator(
                                        decoration: InputDecoration(
                                          labelText: l10n.tr(
                                            fa: 'تاریخ تولد',
                                            en: 'Date of birth',
                                          ),
                                          border: const OutlineInputBorder(),
                                          suffixIcon:
                                              _birthDate == null
                                                  ? const Icon(
                                                    Icons
                                                        .calendar_month_outlined,
                                                  )
                                                  : IconButton(
                                                    tooltip: l10n.tr(
                                                      fa: 'پاک‌کردن تاریخ',
                                                      en: 'Clear date',
                                                    ),
                                                    onPressed:
                                                        () => setState(
                                                          () =>
                                                              _birthDate = null,
                                                        ),
                                                    icon: const Icon(
                                                      Icons.close_rounded,
                                                    ),
                                                  ),
                                        ),
                                        child: Text(
                                          _birthDate == null
                                              ? l10n.tr(
                                                fa: 'انتخاب نشده',
                                                en: 'Not selected',
                                              )
                                              : formatDate(
                                                context,
                                                _birthDate!,
                                              ),
                                        ),
                                      ),
                                    ),
                                    DropdownButtonFormField<String>(
                                      initialValue: _gender,
                                      decoration: InputDecoration(
                                        labelText: l10n.tr(
                                          fa: 'جنسیت',
                                          en: 'Gender',
                                        ),
                                        border: const OutlineInputBorder(),
                                      ),
                                      items: [
                                        DropdownMenuItem(
                                          value: '',
                                          child: Text(
                                            l10n.tr(
                                              fa: 'ترجیح می‌دهم اعلام نکنم',
                                              en: 'Prefer not to say',
                                            ),
                                          ),
                                        ),
                                        DropdownMenuItem(
                                          value: 'male',
                                          child: Text(
                                            l10n.tr(fa: 'مرد', en: 'Male'),
                                          ),
                                        ),
                                        DropdownMenuItem(
                                          value: 'female',
                                          child: Text(
                                            l10n.tr(fa: 'زن', en: 'Female'),
                                          ),
                                        ),
                                        DropdownMenuItem(
                                          value: 'other',
                                          child: Text(
                                            l10n.tr(fa: 'سایر', en: 'Other'),
                                          ),
                                        ),
                                      ],
                                      onChanged:
                                          (value) => setState(
                                            () => _gender = value ?? '',
                                          ),
                                    ),
                                  ],
                                ),
                                SizedBox(height: r.v(14)),
                                _FormSection(
                                  title: l10n.tr(
                                    fa: 'نشانی و محدوده فعالیت',
                                    en: 'Address and location',
                                  ),
                                  icon: Icons.location_on_outlined,
                                  children: [
                                    DropdownButtonFormField<int>(
                                      initialValue: selectedProvinceId,
                                      decoration: InputDecoration(
                                        labelText: l10n.tr(
                                          fa: 'استان',
                                          en: 'Province',
                                        ),
                                        border: const OutlineInputBorder(),
                                      ),
                                      items:
                                          state.provinces
                                              .map(
                                                (item) => DropdownMenuItem<int>(
                                                  value: item.id,
                                                  child: Text(
                                                    item.name,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                  ),
                                                ),
                                              )
                                              .toList(),
                                      validator:
                                          (value) =>
                                              value == null
                                                  ? l10n.tr(
                                                    fa: 'استان را انتخاب کنید',
                                                    en: 'Select a province',
                                                  )
                                                  : null,
                                      onChanged: (value) async {
                                        setState(() {
                                          _provinceId = value;
                                          _countyId = null;
                                          _cityId = null;
                                        });
                                        if (value != null) {
                                          await ref
                                              .read(
                                                profileControllerProvider
                                                    .notifier,
                                              )
                                              .loadCounties(value);
                                        }
                                      },
                                    ),
                                    DropdownButtonFormField<int>(
                                      initialValue: selectedCountyId,
                                      decoration: InputDecoration(
                                        labelText: l10n.tr(
                                          fa: 'شهرستان',
                                          en: 'County',
                                        ),
                                        border: const OutlineInputBorder(),
                                      ),
                                      items:
                                          state.counties
                                              .map(
                                                (item) => DropdownMenuItem<int>(
                                                  value: item.id,
                                                  child: Text(
                                                    item.name,
                                                    overflow:
                                                        TextOverflow.ellipsis,
                                                  ),
                                                ),
                                              )
                                              .toList(),
                                      validator:
                                          (value) =>
                                              value == null
                                                  ? l10n.tr(
                                                    fa: 'شهرستان را انتخاب کنید',
                                                    en: 'Select a county',
                                                  )
                                                  : null,
                                      onChanged: (value) async {
                                        setState(() {
                                          _countyId = value;
                                          _cityId = null;
                                        });
                                        if (value != null) {
                                          await ref
                                              .read(
                                                profileControllerProvider
                                                    .notifier,
                                              )
                                              .loadCities(
                                                provinceId: _provinceId,
                                                countyId: value,
                                              );
                                        }
                                      },
                                    ),
                                    DropdownButtonFormField<int>(
                                      initialValue: selectedCityId,
                                      decoration: InputDecoration(
                                        labelText: l10n.tr(
                                          fa: 'شهر (اختیاری)',
                                          en: 'City (optional)',
                                        ),
                                        border: const OutlineInputBorder(),
                                      ),
                                      items:
                                          state.cities
                                              .map(
                                                (GeoCity item) =>
                                                    DropdownMenuItem<int>(
                                                      value: item.id,
                                                      child: Text(
                                                        item.name,
                                                        overflow:
                                                            TextOverflow
                                                                .ellipsis,
                                                      ),
                                                    ),
                                              )
                                              .toList(),
                                      onChanged:
                                          (value) =>
                                              setState(() => _cityId = value),
                                    ),
                                    FarmTextField(
                                      controller: _addressController,
                                      label: l10n.tr(fa: 'آدرس', en: 'Address'),
                                      maxLines: 3,
                                      validator:
                                          (value) => _required(
                                            value,
                                            l10n.tr(fa: 'آدرس', en: 'Address'),
                                          ),
                                    ),
                                    FarmTextField(
                                      controller: _postalCodeController,
                                      label: l10n.tr(
                                        fa: 'کد پستی',
                                        en: 'Postal code',
                                      ),
                                      keyboardType: TextInputType.number,
                                      validator: _validatePostalCode,
                                    ),
                                  ],
                                ),
                                SizedBox(height: r.v(14)),
                                _FormSection(
                                  title: l10n.tr(
                                    fa: 'درباره من',
                                    en: 'About me',
                                  ),
                                  icon: Icons.notes_rounded,
                                  children: [
                                    FarmTextField(
                                      controller: _bioController,
                                      label: l10n.tr(
                                        fa: 'معرفی کوتاه',
                                        en: 'Short bio',
                                      ),
                                      maxLines: 4,
                                    ),
                                  ],
                                ),
                                if (state.errorMessage != null) ...[
                                  SizedBox(height: r.v(14)),
                                  Material(
                                    color:
                                        Theme.of(
                                          context,
                                        ).colorScheme.errorContainer,
                                    borderRadius: BorderRadius.circular(14),
                                    child: Padding(
                                      padding: const EdgeInsets.all(14),
                                      child: Text(
                                        _profileSaveErrorMessage(
                                          context,
                                          state,
                                        ),
                                        textAlign: TextAlign.center,
                                        style: TextStyle(
                                          color:
                                              Theme.of(
                                                context,
                                              ).colorScheme.onErrorContainer,
                                        ),
                                      ),
                                    ),
                                  ),
                                  if (state.errorTraceId?.isNotEmpty ==
                                      true) ...[
                                    const SizedBox(height: 6),
                                    Text(
                                      l10n.tr(
                                        fa: 'شناسه پیگیری: ${state.errorTraceId}',
                                        en: 'Trace ID: ${state.errorTraceId}',
                                      ),
                                      textAlign: TextAlign.center,
                                      style:
                                          Theme.of(context).textTheme.bodySmall,
                                    ),
                                  ],
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              if (state.isSaving)
                const Positioned(
                  top: 0,
                  left: 0,
                  right: 0,
                  child: LinearProgressIndicator(
                    key: Key('profile-save-progress'),
                    minHeight: 3,
                  ),
                ),
            ],
          );
        },
      ),
    );
  }

  String? _required(String? value, String label) {
    if (value == null || value.trim().isEmpty) {
      return context.l10n.tr(fa: '$label را وارد کنید', en: 'Enter $label');
    }
    return null;
  }

  String? _validateNationalId(String? value) {
    final normalized = toEnglishDigits(value?.trim());
    if (normalized.isEmpty) {
      return context.l10n.tr(
        fa: 'کد ملی را وارد کنید',
        en: 'Enter National ID',
      );
    }
    if (!RegExp(r'^\d{10}$').hasMatch(normalized)) {
      return context.l10n.tr(
        fa: 'کد ملی باید ۱۰ رقم باشد',
        en: 'National ID must be 10 digits',
      );
    }
    return null;
  }

  String? _validatePostalCode(String? value) {
    final normalized = toEnglishDigits(value?.trim());
    if (normalized.isEmpty) return null;
    if (!RegExp(r'^\d{10}$').hasMatch(normalized)) {
      return context.l10n.tr(
        fa: 'کد پستی باید ۱۰ رقم باشد',
        en: 'Postal code must be 10 digits',
      );
    }
    return null;
  }

  String _profileSaveErrorMessage(BuildContext context, ProfileState state) {
    final l10n = context.l10n;
    final code = state.errorCode;
    final message = state.errorMessage ?? '';
    final field = state.errorDetails['field']?.toString();

    if (code == 'PROFILE_NATIONAL_ID_CONFLICT' ||
        code == 'PROFILE_DATA_CONFLICT' ||
        (field == 'national_id' && message.contains('conflict'))) {
      return l10n.tr(
        fa:
            'این کد ملی قبلاً برای حساب دیگری ثبت شده است. برای هر حساب آزمایشی کد ملی جداگانه وارد کنید.',
        en:
            'This National ID is already linked to another account. Use a different National ID for each test account.',
      );
    }

    if (message == 'Invalid national_id') {
      return l10n.tr(
        fa: 'کد ملی باید دقیقاً ۱۰ رقم باشد.',
        en: 'National ID must be exactly 10 digits.',
      );
    }
    if (message == 'Invalid postal_code') {
      return l10n.tr(
        fa: 'کد پستی باید دقیقاً ۱۰ رقم باشد.',
        en: 'Postal code must be exactly 10 digits.',
      );
    }
    if (message == 'Invalid birth_date') {
      return l10n.tr(
        fa: 'تاریخ تولد نمی‌تواند در آینده باشد.',
        en: 'Date of birth cannot be in the future.',
      );
    }
    if (message.contains('_id does not belong to') ||
        message.startsWith('Invalid province_id') ||
        message.startsWith('Invalid county_id') ||
        message.startsWith('Invalid city_id')) {
      return l10n.tr(
        fa:
            'استان، شهرستان و شهر انتخاب‌شده با هم سازگار نیستند؛ دوباره انتخابشان کنید.',
        en:
            'The selected province, county, and city do not match. Select them again.',
      );
    }
    if (message == 'Profile image media file not found') {
      return l10n.tr(
        fa: 'تصویر پروفایل معتبر نیست؛ آن را دوباره انتخاب و بارگذاری کنید.',
        en: 'The profile image is invalid. Select and upload it again.',
      );
    }
    if (code == 'NETWORK_ERROR') {
      return l10n.tr(
        fa: 'ارتباط با سرور برقرار نشد. اتصال را بررسی و دوباره تلاش کنید.',
        en: 'Could not connect to the server. Check the connection and retry.',
      );
    }

    return l10n.tr(
      fa: 'ذخیره پروفایل انجام نشد. اطلاعات را بررسی و دوباره تلاش کنید.',
      en:
          message.isEmpty
              ? 'Could not save the profile. Check the information and retry.'
              : message,
    );
  }
}

class _AvatarEditor extends StatelessWidget {
  const _AvatarEditor({
    required this.avatarUrl,
    required this.onUploaded,
    required this.onClear,
  });

  final String? avatarUrl;
  final void Function(String fileKey, String? publicUrl) onUploaded;
  final VoidCallback? onClear;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final imageUrl = absoluteApiUrl(avatarUrl);

    return _FormSection(
      title: l10n.tr(fa: 'تصویر پروفایل', en: 'Profile image'),
      icon: Icons.account_circle_outlined,
      children: [
        Align(
          child: CircleAvatar(
            radius: 46,
            backgroundImage: imageUrl == null ? null : NetworkImage(imageUrl),
            child:
                imageUrl == null
                    ? const Icon(Icons.person_rounded, size: 48)
                    : null,
          ),
        ),
        MediaUploadButton(
          label: l10n.tr(fa: 'انتخاب تصویر جدید', en: 'Choose a new image'),
          purpose: 'profile_image',
          visibility: 'public',
          allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
          onUploaded: (media) => onUploaded(media.fileKey, media.publicUrl),
        ),
        if (onClear != null)
          TextButton.icon(
            onPressed: onClear,
            icon: const Icon(Icons.delete_outline_rounded),
            label: Text(l10n.tr(fa: 'حذف تصویر', en: 'Remove image')),
          ),
        Text(
          l10n.tr(
            fa: 'تصویر عمومی است؛ حداکثر حجم مجاز ۵ مگابایت است.',
            en: 'The image is public; maximum allowed size is 5 MB.',
          ),
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}

class _FormSection extends StatelessWidget {
  const _FormSection({
    required this.title,
    required this.icon,
    required this.children,
  });

  final String title;
  final IconData icon;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(icon, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            for (var index = 0; index < children.length; index++) ...[
              children[index],
              if (index != children.length - 1) const SizedBox(height: 12),
            ],
          ],
        ),
      ),
    );
  }
}
