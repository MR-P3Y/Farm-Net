import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_back_button.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../../geo/data/geo_api.dart';
import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/auth_models.dart';
import '../state/auth_controller.dart';
import '../state/auth_state.dart';
import 'auth_page_shell.dart';

class RegistrationScreen extends ConsumerStatefulWidget {
  const RegistrationScreen({super.key});

  @override
  ConsumerState<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends ConsumerState<RegistrationScreen> {
  static const _draftStorageKey = 'farmnet_registration_draft_v1';
  static const _draftStorage = FlutterSecureStorage();
  static final _localizedDigitFormatters = <TextInputFormatter>[
    FilteringTextInputFormatter.allow(RegExp(r'[0-9۰-۹٠-٩]')),
    LengthLimitingTextInputFormatter(10),
  ];

  final _formKeys = List.generate(3, (_) => GlobalKey<FormState>());
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _displayNameController = TextEditingController();
  final _nationalIdController = TextEditingController();
  final _addressController = TextEditingController();
  final _postalCodeController = TextEditingController();

  int _step = 0;
  bool _passwordVisible = false;
  bool _confirmPasswordVisible = false;
  bool _isSubmitting = false;
  bool _isLoadingGeo = true;
  String? _geoErrorCode;
  String? _geoErrorTraceId;
  List<GeoProvince> _provinces = const [];
  List<GeoCounty> _counties = const [];
  List<GeoCity> _cities = const [];
  int? _provinceId;
  int? _countyId;
  int? _cityId;
  Timer? _draftTimer;
  bool _draftReady = false;

  @override
  void initState() {
    super.initState();
    for (final controller in [
      _emailController,
      _firstNameController,
      _lastNameController,
      _displayNameController,
      _nationalIdController,
      _addressController,
      _postalCodeController,
    ]) {
      controller.addListener(_scheduleDraftSave);
    }
    Future.microtask(_initializeRegistration);
  }

  @override
  void dispose() {
    _draftTimer?.cancel();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _displayNameController.dispose();
    _nationalIdController.dispose();
    _addressController.dispose();
    _postalCodeController.dispose();
    super.dispose();
  }

  Future<void> _initializeRegistration() async {
    int? restoredProvinceId;
    int? restoredCountyId;
    int? restoredCityId;
    try {
      final raw = await _draftStorage.read(key: _draftStorageKey);
      if (raw != null && raw.isNotEmpty) {
        final data = (jsonDecode(raw) as Map).cast<String, dynamic>();
        _emailController.text = data['email']?.toString() ?? '';
        _firstNameController.text = data['first_name']?.toString() ?? '';
        _lastNameController.text = data['last_name']?.toString() ?? '';
        _displayNameController.text = data['display_name']?.toString() ?? '';
        _nationalIdController.text = data['national_id']?.toString() ?? '';
        _addressController.text = data['address']?.toString() ?? '';
        _postalCodeController.text = data['postal_code']?.toString() ?? '';
        restoredProvinceId = (data['province_id'] as num?)?.toInt();
        restoredCountyId = (data['county_id'] as num?)?.toInt();
        restoredCityId = (data['city_id'] as num?)?.toInt();
      }
    } catch (_) {
      await _draftStorage.delete(key: _draftStorageKey);
    }

    await _loadProvinces();
    if (!mounted) return;
    if (restoredProvinceId != null &&
        _provinces.any((item) => item.id == restoredProvinceId)) {
      await _loadCounties(
        restoredProvinceId,
        preferredCountyId: restoredCountyId,
        preferredCityId: restoredCityId,
      );
    }
    _draftReady = true;
  }

  void _scheduleDraftSave() {
    if (!_draftReady) return;
    _draftTimer?.cancel();
    _draftTimer = Timer(const Duration(milliseconds: 300), _saveDraft);
  }

  Future<void> _saveDraft() async {
    final data = <String, dynamic>{
      'email': _emailController.text.trim(),
      'first_name': _firstNameController.text.trim(),
      'last_name': _lastNameController.text.trim(),
      'display_name': _displayNameController.text.trim(),
      'national_id': toEnglishDigits(_nationalIdController.text.trim()),
      'province_id': _provinceId,
      'county_id': _countyId,
      'city_id': _cityId,
      'address': _addressController.text.trim(),
      'postal_code': toEnglishDigits(_postalCodeController.text.trim()),
    };
    await _draftStorage.write(key: _draftStorageKey, value: jsonEncode(data));
  }

  Future<void> _clearDraft() async {
    _draftTimer?.cancel();
    await _draftStorage.delete(key: _draftStorageKey);
  }

  Future<void> _loadProvinces({bool retryOnce = true}) async {
    if (mounted) {
      setState(() {
        _isLoadingGeo = true;
        _geoErrorCode = null;
        _geoErrorTraceId = null;
      });
    }
    try {
      final rows = await ref.read(geoRepositoryProvider).getProvinces();
      if (!mounted) return;
      setState(() {
        _provinces = rows;
        _isLoadingGeo = false;
      });
    } on GeoApiException catch (error) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted) await _loadProvinces(retryOnce: false);
        return;
      }
      if (!mounted) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = error.error.code;
        _geoErrorTraceId = error.error.traceId;
      });
    } catch (_) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted) await _loadProvinces(retryOnce: false);
        return;
      }
      if (!mounted) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = 'GEO_RESPONSE_INVALID';
        _geoErrorTraceId = null;
      });
    }
  }

  Future<void> _loadCounties(
    int provinceId, {
    int? preferredCountyId,
    int? preferredCityId,
    bool retryOnce = true,
  }) async {
    setState(() {
      _provinceId = provinceId;
      _countyId = null;
      _cityId = null;
      _counties = const [];
      _cities = const [];
      _isLoadingGeo = true;
      _geoErrorCode = null;
      _geoErrorTraceId = null;
    });
    try {
      final rows = await ref
          .read(geoRepositoryProvider)
          .getCounties(provinceId: provinceId);
      if (!mounted || _provinceId != provinceId) return;
      final restoredCountyId =
          preferredCountyId != null &&
                  rows.any((item) => item.id == preferredCountyId)
              ? preferredCountyId
              : null;
      setState(() {
        _counties = rows;
        _countyId = restoredCountyId;
        _isLoadingGeo = restoredCountyId != null;
      });
      if (restoredCountyId != null) {
        await _loadCities(restoredCountyId, preferredCityId: preferredCityId);
      }
      _scheduleDraftSave();
    } on GeoApiException catch (error) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted && _provinceId == provinceId) {
          await _loadCounties(
            provinceId,
            preferredCountyId: preferredCountyId,
            preferredCityId: preferredCityId,
            retryOnce: false,
          );
        }
        return;
      }
      if (!mounted || _provinceId != provinceId) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = error.error.code;
        _geoErrorTraceId = error.error.traceId;
      });
    } catch (_) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted && _provinceId == provinceId) {
          await _loadCounties(
            provinceId,
            preferredCountyId: preferredCountyId,
            preferredCityId: preferredCityId,
            retryOnce: false,
          );
        }
        return;
      }
      if (!mounted || _provinceId != provinceId) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = 'GEO_RESPONSE_INVALID';
        _geoErrorTraceId = null;
      });
    }
  }

  Future<void> _loadCities(
    int countyId, {
    int? preferredCityId,
    bool retryOnce = true,
  }) async {
    setState(() {
      _countyId = countyId;
      _cityId = null;
      _cities = const [];
      _isLoadingGeo = true;
      _geoErrorCode = null;
      _geoErrorTraceId = null;
    });
    try {
      final rows = await ref
          .read(geoRepositoryProvider)
          .getCities(provinceId: _provinceId, countyId: countyId);
      if (!mounted || _countyId != countyId) return;
      final restoredCityId =
          preferredCityId != null &&
                  rows.any((item) => item.id == preferredCityId)
              ? preferredCityId
              : null;
      setState(() {
        _cities = rows;
        _cityId = restoredCityId;
        _isLoadingGeo = false;
      });
      _scheduleDraftSave();
    } on GeoApiException catch (error) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted && _countyId == countyId) {
          await _loadCities(
            countyId,
            preferredCityId: preferredCityId,
            retryOnce: false,
          );
        }
        return;
      }
      if (!mounted || _countyId != countyId) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = error.error.code;
        _geoErrorTraceId = error.error.traceId;
      });
    } catch (_) {
      if (retryOnce) {
        await Future<void>.delayed(const Duration(milliseconds: 650));
        if (mounted && _countyId == countyId) {
          await _loadCities(
            countyId,
            preferredCityId: preferredCityId,
            retryOnce: false,
          );
        }
        return;
      }
      if (!mounted || _countyId != countyId) return;
      setState(() {
        _isLoadingGeo = false;
        _geoErrorCode = 'GEO_RESPONSE_INVALID';
        _geoErrorTraceId = null;
      });
    }
  }

  void _retryGeoLoad() {
    if (_countyId != null) {
      _loadCities(_countyId!);
    } else if (_provinceId != null) {
      _loadCounties(_provinceId!);
    } else {
      _loadProvinces();
    }
  }

  Future<void> _next() async {
    FocusScope.of(context).unfocus();
    ref.read(authControllerProvider.notifier).clearError();
    if (!(_formKeys[_step].currentState?.validate() ?? false)) return;
    if (_step < 2) {
      setState(() => _step += 1);
      return;
    }
    final confirmed = await _showRegistrationReview();
    if (confirmed != true || !mounted) return;
    await _register();
  }

  Future<void> _previous() async {
    FocusScope.of(context).unfocus();
    ref.read(authControllerProvider.notifier).clearError();
    if (_step == 0) {
      context.go('/');
      return;
    }
    setState(() => _step -= 1);
  }

  Future<bool?> _showRegistrationReview() {
    return showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder:
          (context) => _RegistrationReviewSheet(
            fullName:
                '${_firstNameController.text.trim()} ${_lastNameController.text.trim()}',
            email: _emailController.text.trim(),
            nationalId: toEnglishDigits(_nationalIdController.text.trim()),
            province: _selectedProvinceName,
            county: _selectedCountyName,
            city: _selectedCityName,
            address: _addressController.text.trim(),
          ),
    );
  }

  Future<void> _register() async {
    if (_provinceId == null || _countyId == null) return;
    setState(() => _isSubmitting = true);
    final input = EmailRegistrationInput(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      displayName: _optional(_displayNameController.text),
      nationalId: toEnglishDigits(_nationalIdController.text.trim()),
      provinceId: _provinceId!,
      countyId: _countyId!,
      cityId: _cityId,
      address: _addressController.text.trim(),
      postalCode: _optional(toEnglishDigits(_postalCodeController.text.trim())),
    );
    final success = await ref
        .read(authControllerProvider.notifier)
        .registerWithEmail(input);
    if (!mounted) return;
    setState(() => _isSubmitting = false);
    if (success) {
      await _clearDraft();
      TextInput.finishAutofillContext(shouldSave: true);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          key: const Key('registration-success'),
          behavior: SnackBarBehavior.floating,
          duration: const Duration(milliseconds: 900),
          content: Row(
            children: [
              const Icon(Icons.check_circle_rounded, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  context.l10n.tr(
                    fa: 'حساب شما با موفقیت ساخته شد.',
                    en: 'Your account was created successfully.',
                  ),
                ),
              ),
            ],
          ),
        ),
      );
      await Future<void>.delayed(const Duration(milliseconds: 700));
      if (mounted) context.go('/home');
    }
  }

  String get _selectedProvinceName =>
      _provinces
          .where((item) => item.id == _provinceId)
          .map((item) => item.name)
          .firstOrNull ??
      '-';

  String get _selectedCountyName =>
      _counties
          .where((item) => item.id == _countyId)
          .map((item) => item.name)
          .firstOrNull ??
      '-';

  String? get _selectedCityName =>
      _cities
          .where((item) => item.id == _cityId)
          .map((item) => item.name)
          .firstOrNull;

  String? _optional(String value) {
    final normalized = value.trim();
    return normalized.isEmpty ? null : normalized;
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authControllerProvider);
    final l10n = context.l10n;
    final titles = [
      l10n.tr(fa: 'اطلاعات حساب', en: 'Account'),
      l10n.tr(fa: 'مشخصات هویتی', en: 'Identity'),
      l10n.tr(fa: 'محل سکونت', en: 'Location'),
    ];

    final authTheme = AppTheme.dark(Localizations.localeOf(context));
    final glassAuthTheme = authTheme.copyWith(
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withValues(alpha: .07),
        labelStyle: const TextStyle(color: Colors.white70),
        hintStyle: const TextStyle(color: Colors.white60),
        prefixIconColor: Colors.white70,
        suffixIconColor: Colors.white70,
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: .18)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.white, width: 1.2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.redAccent),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Colors.redAccent, width: 1.2),
        ),
        errorStyle: const TextStyle(color: Color(0xFFFFB4AB)),
      ),
      iconTheme: const IconThemeData(color: Colors.white70),
    );

    return PopScope(
      canPop: _step == 0,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop && _step > 0) _previous();
      },
      child: Theme(
        data: glassAuthTheme,
        child: AuthPageShell(
          maxWidth: 440,
          mobileHorizontalPadding: 14,
          mobileAlignment: Alignment.topCenter,
          layoutKey: const Key('registration-layout-stack'),
          backgroundKey: const Key('registration-background-image'),
          bottomPanel: FarmGlassCard(
            key: const Key('registration-action-panel'),
            opacity: .12,
            blur: 16,
            borderRadius: 28,
            padding: const EdgeInsets.all(10),
            child: _RegistrationActions(
              step: _step,
              isSubmitting: _isSubmitting,
              onPrimary: _next,
              onSecondary: _previous,
            ),
          ),
          child: FarmGlassCard(
            key: const Key('registration-form-card'),
            opacity: .1,
            blur: 16,
            borderRadius: 28,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 18),
            child: AnimatedSize(
              duration: const Duration(milliseconds: 260),
              curve: Curves.easeOutCubic,
              alignment: Alignment.topCenter,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _Header(onBack: _previous, compact: true),
                  const SizedBox(height: 14),
                  _StepHeader(step: _step, title: titles[_step]),
                  const SizedBox(height: 12),
                  if (_isSubmitting)
                    const LinearProgressIndicator(
                      key: Key('registration-submit-progress'),
                      minHeight: 3,
                    ),
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 220),
                    switchInCurve: Curves.easeOutCubic,
                    switchOutCurve: Curves.easeInCubic,
                    transitionBuilder: (child, animation) {
                      return FadeTransition(
                        opacity: animation,
                        child: SizeTransition(
                          sizeFactor: animation,
                          alignment: Alignment.topCenter,
                          child: child,
                        ),
                      );
                    },
                    child: KeyedSubtree(
                      key: ValueKey('registration-step-$_step'),
                      child: switch (_step) {
                        0 => _accountStep(l10n),
                        1 => _identityStep(l10n),
                        _ => _locationStep(l10n),
                      },
                    ),
                  ),
                  if (auth.errorMessage != null)
                    _ErrorPanel(
                      message: _registrationError(context, auth),
                      traceId: auth.errorTraceId,
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _accountStep(AppLocalizations l10n) {
    return Form(
      key: _formKeys[0],
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: AutofillGroup(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _StepIntro(
                icon: Icons.lock_person_outlined,
                text: l10n.tr(
                  fa: 'ایمیل معتبر و یک رمز امن برای ورود انتخاب کنید.',
                  en: 'Choose a valid email and a secure sign-in password.',
                ),
              ),
              const SizedBox(height: 16),
              FarmTextField(
                controller: _emailController,
                label: l10n.tr(fa: 'ایمیل', en: 'Email'),
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
                prefixIcon: Icons.alternate_email_rounded,
                autofillHints: const [
                  AutofillHints.email,
                  AutofillHints.username,
                ],
                autocorrect: false,
                enableSuggestions: false,
                validator: (value) => _validateEmail(l10n, value),
              ),
              const SizedBox(height: 12),
              FarmTextField(
                controller: _passwordController,
                label: l10n.password,
                obscureText: !_passwordVisible,
                textInputAction: TextInputAction.next,
                prefixIcon: Icons.lock_outline_rounded,
                autofillHints: const [AutofillHints.newPassword],
                autocorrect: false,
                enableSuggestions: false,
                onChanged: (_) => setState(() {}),
                suffixIcon: IconButton(
                  onPressed:
                      () =>
                          setState(() => _passwordVisible = !_passwordVisible),
                  icon: Icon(
                    _passwordVisible
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                ),
                validator: (value) => _validatePassword(l10n, value),
              ),
              const SizedBox(height: 8),
              _PasswordStrength(password: _passwordController.text),
              const SizedBox(height: 12),
              FarmTextField(
                controller: _confirmPasswordController,
                label: l10n.tr(fa: 'تکرار رمز عبور', en: 'Confirm password'),
                obscureText: !_confirmPasswordVisible,
                textInputAction: TextInputAction.done,
                prefixIcon: Icons.lock_reset_rounded,
                autofillHints: const [AutofillHints.newPassword],
                autocorrect: false,
                enableSuggestions: false,
                suffixIcon: IconButton(
                  onPressed:
                      () => setState(
                        () =>
                            _confirmPasswordVisible = !_confirmPasswordVisible,
                      ),
                  icon: Icon(
                    _confirmPasswordVisible
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                ),
                validator:
                    (value) =>
                        value != _passwordController.text
                            ? l10n.tr(
                              fa: 'تکرار رمز عبور یکسان نیست',
                              en: 'Passwords do not match',
                            )
                            : null,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _identityStep(AppLocalizations l10n) {
    return Form(
      key: _formKeys[1],
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _StepIntro(
              icon: Icons.badge_outlined,
              text: l10n.tr(
                fa:
                    'این مشخصات برای پروفایل و فرایندهای تأیید هویت استفاده می‌شود.',
                en: 'These details are used for your profile and verification.',
              ),
            ),
            const SizedBox(height: 16),
            FarmTextField(
              controller: _firstNameController,
              label: l10n.tr(fa: 'نام', en: 'First name'),
              textInputAction: TextInputAction.next,
              prefixIcon: Icons.person_outline_rounded,
              validator:
                  (value) =>
                      _required(l10n, value, fa: 'نام', en: 'first name'),
            ),
            const SizedBox(height: 12),
            FarmTextField(
              controller: _lastNameController,
              label: l10n.tr(fa: 'نام خانوادگی', en: 'Last name'),
              textInputAction: TextInputAction.next,
              prefixIcon: Icons.person_outline_rounded,
              validator:
                  (value) => _required(
                    l10n,
                    value,
                    fa: 'نام خانوادگی',
                    en: 'last name',
                  ),
            ),
            const SizedBox(height: 12),
            FarmTextField(
              controller: _displayNameController,
              label: l10n.tr(
                fa: 'نام نمایشی (اختیاری)',
                en: 'Display name (optional)',
              ),
              textInputAction: TextInputAction.next,
              prefixIcon: Icons.account_circle_outlined,
            ),
            const SizedBox(height: 12),
            FarmTextField(
              controller: _nationalIdController,
              label: l10n.tr(fa: 'کد ملی', en: 'National ID'),
              keyboardType: TextInputType.number,
              textInputAction: TextInputAction.done,
              prefixIcon: Icons.credit_card_rounded,
              maxLength: 10,
              inputFormatters: _localizedDigitFormatters,
              validator: (value) => _validateNationalId(l10n, value),
            ),
            const SizedBox(height: 8),
            _PrivacyNote(
              text: l10n.tr(
                fa:
                    'کد ملی فقط برای تأیید هویت استفاده می‌شود، عمومی نمایش داده نمی‌شود و باید متعلق به همین حساب باشد.',
                en:
                    'National ID is used only for identity verification, is not shown publicly, and must belong to this account.',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _locationStep(AppLocalizations l10n) {
    return Form(
      key: _formKeys[2],
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _StepIntro(
              icon: Icons.location_on_outlined,
              text: l10n.tr(
                fa: 'محدوده فعالیت و نشانی اصلی پروفایل را مشخص کنید.',
                en: 'Set your main profile location and address.',
              ),
            ),
            if (_isLoadingGeo) ...[
              const SizedBox(height: 12),
              const LinearProgressIndicator(
                key: Key('registration-geo-progress'),
                minHeight: 3,
              ),
            ],
            if (_geoErrorCode != null) ...[
              const SizedBox(height: 12),
              _InlineGeoError(
                errorCode: _geoErrorCode!,
                traceId: _geoErrorTraceId,
                onRetry: _retryGeoLoad,
              ),
            ],
            const SizedBox(height: 16),
            _GeoPickerField(
              key: ValueKey('registration-province-$_provinceId'),
              value: _provinceId,
              label: l10n.tr(fa: 'استان', en: 'Province'),
              placeholder: l10n.tr(fa: 'انتخاب استان', en: 'Select province'),
              icon: Icons.map_outlined,
              enabled: !_isLoadingGeo && _provinces.isNotEmpty,
              items:
                  _provinces
                      .map((item) => _GeoChoice(item.id, item.name))
                      .toList(),
              onChanged: (value) {
                if (value != null) _loadCounties(value);
              },
              validator:
                  (value) =>
                      value == null
                          ? l10n.tr(
                            fa: 'استان را انتخاب کنید',
                            en: 'Select a province',
                          )
                          : null,
            ),
            const SizedBox(height: 12),
            _GeoPickerField(
              key: ValueKey('registration-county-$_provinceId-$_countyId'),
              value: _countyId,
              label: l10n.tr(fa: 'شهرستان', en: 'County'),
              placeholder: l10n.tr(fa: 'انتخاب شهرستان', en: 'Select county'),
              icon: Icons.location_city_outlined,
              enabled:
                  !_isLoadingGeo && _provinceId != null && _counties.isNotEmpty,
              items:
                  _counties
                      .map((item) => _GeoChoice(item.id, item.name))
                      .toList(),
              onChanged: (value) {
                if (value != null) _loadCities(value);
              },
              validator:
                  (value) =>
                      value == null
                          ? l10n.tr(
                            fa: 'شهرستان را انتخاب کنید',
                            en: 'Select a county',
                          )
                          : null,
            ),
            const SizedBox(height: 12),
            _GeoPickerField(
              key: ValueKey('registration-city-$_countyId-$_cityId'),
              value: _cityId,
              label: l10n.tr(fa: 'شهر (اختیاری)', en: 'City (optional)'),
              placeholder: l10n.tr(
                fa: 'انتخاب شهر (اختیاری)',
                en: 'Select city (optional)',
              ),
              icon: Icons.apartment_outlined,
              enabled: !_isLoadingGeo && _countyId != null,
              allowClear: true,
              items:
                  _cities
                      .map((item) => _GeoChoice(item.id, item.name))
                      .toList(),
              onChanged: (value) {
                setState(() => _cityId = value);
                _scheduleDraftSave();
              },
            ),
            const SizedBox(height: 12),
            FarmTextField(
              controller: _addressController,
              label: l10n.tr(fa: 'آدرس', en: 'Address'),
              maxLines: 3,
              prefixIcon: Icons.home_outlined,
              validator:
                  (value) => _required(l10n, value, fa: 'آدرس', en: 'address'),
            ),
            const SizedBox(height: 12),
            FarmTextField(
              controller: _postalCodeController,
              label: l10n.tr(
                fa: 'کد پستی (اختیاری)',
                en: 'Postal code (optional)',
              ),
              keyboardType: TextInputType.number,
              prefixIcon: Icons.local_post_office_outlined,
              maxLength: 10,
              inputFormatters: _localizedDigitFormatters,
              validator: (value) => _validatePostalCode(l10n, value),
            ),
            const SizedBox(height: 8),
            _DraftNote(),
          ],
        ),
      ),
    );
  }

  String? _validateEmail(AppLocalizations l10n, String? value) {
    final email = value?.trim() ?? '';
    if (email.isEmpty) {
      return l10n.tr(fa: 'ایمیل را وارد کنید', en: 'Enter your email');
    }
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(email)) {
      return l10n.tr(fa: 'ایمیل معتبر نیست', en: 'Enter a valid email');
    }
    return null;
  }

  String? _validatePassword(AppLocalizations l10n, String? value) {
    if (value == null || value.length < 8) {
      return l10n.tr(
        fa: 'رمز عبور باید حداقل ۸ نویسه باشد',
        en: 'Password must be at least 8 characters',
      );
    }
    return null;
  }

  String? _required(
    AppLocalizations l10n,
    String? value, {
    required String fa,
    required String en,
  }) {
    if (value == null || value.trim().isEmpty) {
      return l10n.tr(fa: '$fa را وارد کنید', en: 'Enter $en');
    }
    return null;
  }

  String? _validateNationalId(AppLocalizations l10n, String? value) {
    final normalized = toEnglishDigits(value?.trim());
    if (!RegExp(r'^\d{10}$').hasMatch(normalized)) {
      return l10n.tr(
        fa: 'کد ملی باید دقیقاً ۱۰ رقم باشد',
        en: 'National ID must be exactly 10 digits',
      );
    }
    return null;
  }

  String? _validatePostalCode(AppLocalizations l10n, String? value) {
    final normalized = toEnglishDigits(value?.trim());
    if (normalized.isEmpty) return null;
    if (!RegExp(r'^\d{10}$').hasMatch(normalized)) {
      return l10n.tr(
        fa: 'کد پستی باید دقیقاً ۱۰ رقم باشد',
        en: 'Postal code must be exactly 10 digits',
      );
    }
    return null;
  }

  String _registrationError(BuildContext context, AuthState state) {
    final l10n = context.l10n;
    return switch (state.errorCode) {
      'AUTH_USER_ALREADY_EXISTS' => l10n.tr(
        fa: 'این ایمیل قبلاً ثبت شده است؛ وارد حساب شوید.',
        en: 'This email is already registered. Sign in instead.',
      ),
      'PROFILE_NATIONAL_ID_CONFLICT' || 'PROFILE_DATA_CONFLICT' => l10n.tr(
        fa: 'این کد ملی قبلاً برای حساب دیگری ثبت شده است.',
        en: 'This National ID is already linked to another account.',
      ),
      'VALIDATION_ERROR' => l10n.tr(
        fa: 'یکی از اطلاعات واردشده معتبر نیست؛ فیلدها را بررسی کنید.',
        en: 'Some registration information is invalid. Check the fields.',
      ),
      'NETWORK_ERROR' => l10n.tr(
        fa: 'ارتباط با سرور برقرار نشد. اتصال را بررسی و دوباره تلاش کنید.',
        en: 'Could not connect to the server. Check the connection and retry.',
      ),
      _ => l10n.tr(
        fa: 'ثبت‌نام انجام نشد. اطلاعات را بررسی و دوباره تلاش کنید.',
        en: state.errorMessage ?? 'Registration failed. Try again.',
      ),
    };
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onBack, required this.compact});

  final VoidCallback onBack;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Row(
      children: [
        FarmBackButton(
          color: Colors.white,
          fallbackLocation: '/login',
          onPressed: onBack,
        ),
        SizedBox(width: compact ? 8 : 12),
        Expanded(
          child: Text(
            l10n.tr(fa: 'ساخت حساب فارم نت', en: 'Create Farm Net account'),
            style: (compact
                    ? Theme.of(context).textTheme.titleMedium
                    : Theme.of(context).textTheme.titleLarge)
                ?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                  shadows: const [Shadow(color: Colors.black45, blurRadius: 8)],
                ),
          ),
        ),
        Icon(Icons.eco_rounded, color: Colors.white, size: compact ? 27 : 32),
      ],
    );
  }
}

class _StepHeader extends StatelessWidget {
  const _StepHeader({required this.step, required this.title});

  final int step;
  final String title;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                title,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
            ),
            Text(
              l10n.tr(
                fa: 'مرحله ${toPersianDigits(step + 1)} از ۳',
                en: 'Step ${step + 1} of 3',
              ),
              style: Theme.of(context).textTheme.labelLarge,
            ),
          ],
        ),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(99),
          child: LinearProgressIndicator(value: (step + 1) / 3, minHeight: 7),
        ),
      ],
    );
  }
}

class _StepIntro extends StatelessWidget {
  const _StepIntro({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.primaryContainer.withValues(alpha: .55),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Icon(icon, color: colors.primary),
            const SizedBox(width: 10),
            Expanded(child: Text(text)),
          ],
        ),
      ),
    );
  }
}

class _ErrorPanel extends StatelessWidget {
  const _ErrorPanel({required this.message, this.traceId});

  final String message;
  final String? traceId;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      key: const Key('registration-error'),
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.errorContainer,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        children: [
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: colors.onErrorContainer),
          ),
          if (traceId?.isNotEmpty == true) ...[
            const SizedBox(height: 4),
            Text(
              context.l10n.tr(
                fa: 'شناسه پیگیری: $traceId',
                en: 'Trace ID: $traceId',
              ),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      ),
    );
  }
}

class _InlineGeoError extends StatelessWidget {
  const _InlineGeoError({
    required this.errorCode,
    required this.onRetry,
    this.traceId,
  });

  final String errorCode;
  final VoidCallback onRetry;
  final String? traceId;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final message = switch (errorCode) {
      'NETWORK_ERROR' => l10n.tr(
        fa: 'ارتباط با سرور مناطق برقرار نشد. اتصال را بررسی کنید.',
        en: 'Could not reach the location server. Check your connection.',
      ),
      'GEO_RESPONSE_INVALID' => l10n.tr(
        fa: 'پاسخ مناطق قابل پردازش نبود. دوباره تلاش کنید.',
        en: 'The location response could not be processed. Try again.',
      ),
      _ => l10n.tr(
        fa: 'سرور مناطق پاسخ نداد. دوباره تلاش کنید.',
        en: 'The location server did not respond. Try again.',
      ),
    };
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Row(
          children: [
            Icon(
              errorCode == 'NETWORK_ERROR'
                  ? Icons.wifi_off_rounded
                  : Icons.location_off_outlined,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(message),
                  if (traceId?.isNotEmpty == true)
                    Text(
                      l10n.tr(
                        fa: 'شناسه پیگیری: $traceId',
                        en: 'Trace ID: $traceId',
                      ),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                ],
              ),
            ),
            TextButton(onPressed: onRetry, child: Text(l10n.retry)),
          ],
        ),
      ),
    );
  }
}

class _PasswordStrength extends StatelessWidget {
  const _PasswordStrength({required this.password});

  final String password;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final checks = [
      password.length >= 8,
      password.length >= 12,
      RegExp(r'[A-Za-z]').hasMatch(password),
      RegExp(r'\d').hasMatch(password),
      RegExp(r'[^A-Za-z0-9]').hasMatch(password),
    ];
    final score = checks.where((value) => value).length;
    final colors = Theme.of(context).colorScheme;
    final (label, color) = switch (score) {
      <= 1 => (l10n.tr(fa: 'ضعیف', en: 'Weak'), colors.error),
      <= 3 => (l10n.tr(fa: 'متوسط', en: 'Medium'), colors.tertiary),
      _ => (l10n.tr(fa: 'قوی', en: 'Strong'), colors.primary),
    };
    return Semantics(
      label: l10n.tr(
        fa: 'قدرت رمز عبور $label',
        en: 'Password strength $label',
      ),
      child: Column(
        key: const Key('registration-password-strength'),
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  l10n.tr(fa: 'قدرت رمز عبور', en: 'Password strength'),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
              Text(
                label,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          ClipRRect(
            borderRadius: BorderRadius.circular(99),
            child: LinearProgressIndicator(
              value: password.isEmpty ? 0 : score / checks.length,
              minHeight: 6,
              color: color,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            l10n.tr(
              fa: 'برای رمز قوی‌تر از حروف، عدد و نشانه استفاده کنید.',
              en: 'Use letters, numbers, and a symbol for a stronger password.',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

class _PrivacyNote extends StatelessWidget {
  const _PrivacyNote({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.secondaryContainer.withValues(alpha: .55),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.privacy_tip_outlined, color: colors.secondary),
            const SizedBox(width: 9),
            Expanded(
              child: Text(text, style: Theme.of(context).textTheme.bodySmall),
            ),
          ],
        ),
      ),
    );
  }
}

class _DraftNote extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          Icons.save_outlined,
          size: 18,
          color: Theme.of(context).colorScheme.primary,
        ),
        const SizedBox(width: 7),
        Expanded(
          child: Text(
            context.l10n.tr(
              fa:
                  'پیش‌نویس در فضای امن همین دستگاه نگه داشته می‌شود؛ رمز عبور هرگز ذخیره نمی‌شود.',
              en:
                  'The draft is kept in secure storage on this device; passwords are never saved.',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    );
  }
}

class _GeoChoice {
  const _GeoChoice(this.id, this.name);

  final int id;
  final String name;
}

class _GeoPickerField extends StatelessWidget {
  const _GeoPickerField({
    required this.value,
    required this.label,
    required this.placeholder,
    required this.icon,
    required this.items,
    required this.enabled,
    required this.onChanged,
    this.validator,
    this.allowClear = false,
    super.key,
  });

  final int? value;
  final String label;
  final String placeholder;
  final IconData icon;
  final List<_GeoChoice> items;
  final bool enabled;
  final ValueChanged<int?> onChanged;
  final String? Function(int?)? validator;
  final bool allowClear;

  @override
  Widget build(BuildContext context) {
    return FormField<int>(
      initialValue: value,
      validator: validator,
      builder: (field) {
        final selected =
            items.where((item) => item.id == field.value).firstOrNull;
        Future<void> choose() async {
          if (!enabled) return;
          final result = await showModalBottomSheet<int>(
            context: context,
            useSafeArea: true,
            isScrollControlled: true,
            showDragHandle: true,
            builder: (_) => _GeoSearchSheet(title: label, items: items),
          );
          if (result == null || !context.mounted) return;
          field.didChange(result);
          onChanged(result);
        }

        return InkWell(
          onTap: choose,
          borderRadius: BorderRadius.circular(14),
          child: InputDecorator(
            isEmpty: selected == null,
            decoration: InputDecoration(
              labelText: label,
              hintText: placeholder,
              floatingLabelBehavior: FloatingLabelBehavior.always,
              errorText: field.errorText,
              enabled: enabled,
              prefixIcon: Icon(icon),
              suffixIcon:
                  allowClear && field.value != null
                      ? IconButton(
                        tooltip: context.l10n.tr(fa: 'پاک کردن', en: 'Clear'),
                        onPressed: () {
                          field.didChange(null);
                          onChanged(null);
                        },
                        icon: const Icon(Icons.close_rounded),
                      )
                      : const Icon(Icons.search_rounded),
            ),
            child:
                selected == null
                    ? null
                    : Text(
                      selected.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
          ),
        );
      },
    );
  }
}

class _GeoSearchSheet extends StatefulWidget {
  const _GeoSearchSheet({required this.title, required this.items});

  final String title;
  final List<_GeoChoice> items;

  @override
  State<_GeoSearchSheet> createState() => _GeoSearchSheetState();
}

class _GeoSearchSheetState extends State<_GeoSearchSheet> {
  final _searchController = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final query = _query.trim().toLowerCase();
    final filtered =
        query.isEmpty
            ? widget.items
            : widget.items
                .where((item) => item.name.toLowerCase().contains(query))
                .toList();
    return FractionallySizedBox(
      heightFactor: .78,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              widget.title,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            TextField(
              key: const Key('registration-geo-search'),
              controller: _searchController,
              autofocus: true,
              onChanged: (value) => setState(() => _query = value),
              decoration: InputDecoration(
                hintText: context.l10n.tr(
                  fa: 'نام منطقه را جست‌وجو کنید',
                  en: 'Search locations',
                ),
                prefixIcon: const Icon(Icons.search_rounded),
                suffixIcon:
                    _query.isEmpty
                        ? null
                        : IconButton(
                          onPressed: () {
                            _searchController.clear();
                            setState(() => _query = '');
                          },
                          icon: const Icon(Icons.close_rounded),
                        ),
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child:
                  filtered.isEmpty
                      ? Center(
                        child: Text(
                          context.l10n.tr(
                            fa: 'موردی پیدا نشد',
                            en: 'No location found',
                          ),
                        ),
                      )
                      : ListView.separated(
                        itemCount: filtered.length,
                        separatorBuilder: (_, _) => const Divider(height: 1),
                        itemBuilder: (context, index) {
                          final item = filtered[index];
                          return ListTile(
                            title: Text(item.name),
                            leading: const Icon(Icons.location_on_outlined),
                            onTap: () => Navigator.pop(context, item.id),
                          );
                        },
                      ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RegistrationReviewSheet extends StatelessWidget {
  const _RegistrationReviewSheet({
    required this.fullName,
    required this.email,
    required this.nationalId,
    required this.province,
    required this.county,
    required this.city,
    required this.address,
  });

  final String fullName;
  final String email;
  final String nationalId;
  final String province;
  final String county;
  final String? city;
  final String address;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final maskedNationalId =
        nationalId.length >= 4
            ? '••••••${nationalId.substring(nationalId.length - 4)}'
            : nationalId;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 620),
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(18, 0, 18, 20),
          child: Column(
            key: const Key('registration-review-sheet'),
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Icon(
                Icons.fact_check_outlined,
                size: 42,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 8),
              Text(
                l10n.tr(fa: 'مرور اطلاعات ثبت‌نام', en: 'Review registration'),
                textAlign: TextAlign.center,
                style: Theme.of(
                  context,
                ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              Text(
                l10n.tr(
                  fa: 'پیش از ساخت حساب، اطلاعات اصلی را بررسی کنید.',
                  en: 'Check the main details before creating your account.',
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 18),
              _ReviewRow(
                label: l10n.tr(fa: 'نام', en: 'Name'),
                value: fullName,
              ),
              _ReviewRow(
                label: l10n.tr(fa: 'ایمیل', en: 'Email'),
                value: email,
              ),
              _ReviewRow(
                label: l10n.tr(fa: 'کد ملی', en: 'National ID'),
                value: maskedNationalId,
              ),
              _ReviewRow(
                label: l10n.tr(fa: 'استان', en: 'Province'),
                value: province,
              ),
              _ReviewRow(
                label: l10n.tr(fa: 'شهرستان', en: 'County'),
                value: county,
              ),
              if (city?.isNotEmpty == true)
                _ReviewRow(label: l10n.tr(fa: 'شهر', en: 'City'), value: city!),
              _ReviewRow(
                label: l10n.tr(fa: 'آدرس', en: 'Address'),
                value: address,
              ),
              const SizedBox(height: 12),
              _PrivacyNote(
                text: l10n.tr(
                  fa: 'کد ملی در بخش‌های عمومی پروفایل نمایش داده نمی‌شود.',
                  en: 'National ID is not displayed in public profile areas.',
                ),
              ),
              const SizedBox(height: 16),
              LayoutBuilder(
                builder: (context, constraints) {
                  final edit = FarmButton(
                    label: l10n.tr(fa: 'ویرایش', en: 'Edit'),
                    icon: Icons.edit_outlined,
                    variant: FarmButtonVariant.secondary,
                    expand: true,
                    onPressed: () => Navigator.pop(context, false),
                  );
                  final confirm = FarmButton(
                    key: const Key('registration-review-confirm'),
                    label: l10n.tr(
                      fa: 'تأیید و ساخت حساب',
                      en: 'Confirm and create',
                    ),
                    icon: Icons.check_rounded,
                    expand: true,
                    onPressed: () => Navigator.pop(context, true),
                  );
                  if (constraints.maxWidth < 420) {
                    return Column(
                      children: [confirm, const SizedBox(height: 8), edit],
                    );
                  }
                  return Row(
                    children: [
                      Expanded(child: edit),
                      const SizedBox(width: 10),
                      Expanded(flex: 2, child: confirm),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ReviewRow extends StatelessWidget {
  const _ReviewRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 92,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

class _RegistrationActions extends StatelessWidget {
  const _RegistrationActions({
    required this.step,
    required this.isSubmitting,
    required this.onPrimary,
    required this.onSecondary,
  });

  final int step;
  final bool isSubmitting;
  final VoidCallback onPrimary;
  final VoidCallback onSecondary;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final primaryLabel =
        step == 2
            ? l10n.tr(fa: 'مرور اطلاعات', en: 'Review details')
            : l10n.tr(fa: 'مرحله بعد', en: 'Next step');
    final secondaryLabel =
        step == 0
            ? l10n.tr(fa: 'بازگشت به ورود', en: 'Back to login')
            : l10n.back;
    final primary = SizedBox(
      height: 54,
      child: FarmButton(
        key: const Key('registration-primary-action'),
        label: primaryLabel,
        icon:
            step == 2 ? Icons.fact_check_outlined : Icons.arrow_forward_rounded,
        isLoading: isSubmitting,
        expand: true,
        onPressed: onPrimary,
      ),
    );
    final secondary = SizedBox(
      height: 54,
      child: FarmButton(
        key: const Key('registration-secondary-action'),
        label: secondaryLabel,
        icon: step == 0 ? Icons.login_rounded : Icons.arrow_back_rounded,
        variant: FarmButtonVariant.secondary,
        expand: true,
        onPressed: isSubmitting ? null : onSecondary,
      ),
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        double requiredButtonWidth(String label) {
          final buttonTextStyle =
              Theme.of(
                context,
              ).filledButtonTheme.style?.textStyle?.resolve({}) ??
              Theme.of(context).textTheme.labelLarge ??
              const TextStyle();
          final textPainter = TextPainter(
            text: TextSpan(text: label, style: buttonTextStyle),
            maxLines: 1,
            textDirection: Directionality.of(context),
            textScaler: MediaQuery.textScalerOf(context),
          )..layout();

          // Icon, icon gap and conservative horizontal button padding.
          return textPainter.width + 19 + 8 + 64;
        }

        final minimumSecondaryWidth = requiredButtonWidth(
          secondaryLabel,
        ).clamp(220.0, double.infinity);
        final minimumPrimaryWidth = requiredButtonWidth(
          primaryLabel,
        ).clamp(180.0, double.infinity);
        final availableWidthPerButton = (constraints.maxWidth - 12) / 2;
        final widestMinimumButtonWidth =
            minimumSecondaryWidth > minimumPrimaryWidth
                ? minimumSecondaryWidth
                : minimumPrimaryWidth;
        final canShowSideBySide =
            constraints.maxWidth >= 480 &&
            availableWidthPerButton >= widestMinimumButtonWidth;

        if (!canShowSideBySide) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [primary, const SizedBox(height: 10), secondary],
          );
        }
        return Row(
          children: [
            Expanded(child: secondary),
            const SizedBox(width: 12),
            Expanded(child: primary),
          ],
        );
      },
    );
  }
}
