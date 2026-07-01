import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../data/consultant_models.dart';
import '../state/consultant_profile_controller.dart';

class MyConsultantProfileScreen extends ConsumerStatefulWidget {
  const MyConsultantProfileScreen({super.key});

  @override
  ConsumerState<MyConsultantProfileScreen> createState() =>
      _MyConsultantProfileScreenState();
}

class _MyConsultantProfileScreenState
    extends ConsumerState<MyConsultantProfileScreen> {
  final _displayNameController = TextEditingController();
  final _titleController = TextEditingController();
  final _bioController = TextEditingController();
  final _experienceController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _provinceController = TextEditingController();
  final _cityController = TextEditingController();

  final Set<int> _selectedSpecialtyIds = {};
  bool _loaded = false;
  bool _filled = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(consultantProfileControllerProvider.notifier).load();
    });
  }

  @override
  void dispose() {
    _displayNameController.dispose();
    _titleController.dispose();
    _bioController.dispose();
    _experienceController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _provinceController.dispose();
    _cityController.dispose();
    super.dispose();
  }

  void _fillOnce(ConsultantProfileModel? profile) {
    if (_filled || profile == null) return;
    _filled = true;

    _displayNameController.text = profile.displayName ?? profile.name ?? '';
    _titleController.text = profile.title ?? '';
    _bioController.text = profile.bio ?? '';
    _experienceController.text = profile.experienceYears?.toString() ?? '';
    _phoneController.text = profile.phone ?? '';
    _emailController.text = profile.email ?? '';
    _provinceController.text = profile.provinceName ?? '';
    _cityController.text = profile.cityName ?? '';

    _selectedSpecialtyIds
      ..clear()
      ..addAll(profile.specialties.map((item) => item.id));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(consultantProfileControllerProvider);
    final profile = state.profile;
    _fillOnce(profile);

    return Scaffold(
      appBar: const FarmAppBar(title: 'پروفایل مشاور من'),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            if (state.isLoading) {
              return const FarmLoadingView();
            }

            return Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 760),
                child: ListView(
                  padding: r.pagePadding(),
                  children: [
                    _HeaderCard(profile: profile),
                    SizedBox(height: r.v(12)),
                    Card(
                      child: Padding(
                        padding: EdgeInsets.all(r.s(18)),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            FarmTextField(
                              controller: _displayNameController,
                              label: 'نام نمایشی',
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _titleController,
                              label: 'عنوان تخصصی',
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _bioController,
                              label: 'درباره شما و تجربه کاری',
                              maxLines: 5,
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _experienceController,
                              label: 'سال تجربه',
                              keyboardType: TextInputType.number,
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _phoneController,
                              label: 'شماره تماس',
                              keyboardType: TextInputType.phone,
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _emailController,
                              label: 'ایمیل',
                              keyboardType: TextInputType.emailAddress,
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _provinceController,
                              label: 'استان',
                            ),
                            SizedBox(height: r.v(12)),
                            FarmTextField(
                              controller: _cityController,
                              label: 'شهر',
                            ),
                            SizedBox(height: r.v(16)),
                            Text(
                              'تخصص‌ها',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            SizedBox(height: r.v(8)),
                            _SpecialtySelector(
                              specialties: state.specialties,
                              selectedIds: _selectedSpecialtyIds,
                              onToggle: (specialtyId) {
                                setState(() {
                                  if (_selectedSpecialtyIds.contains(
                                    specialtyId,
                                  )) {
                                    _selectedSpecialtyIds.remove(specialtyId);
                                  } else {
                                    _selectedSpecialtyIds.add(specialtyId);
                                  }
                                });
                              },
                            ),
                            if (state.errorMessage != null) ...[
                              SizedBox(height: r.v(12)),
                              _MessageBox(
                                message: state.errorMessage!,
                                isError: true,
                              ),
                            ],
                            if (state.successMessage != null) ...[
                              SizedBox(height: r.v(12)),
                              _MessageBox(
                                message: state.successMessage!,
                                isError: false,
                              ),
                            ],
                            SizedBox(height: r.v(20)),
                            FarmButton(
                              label: 'ذخیره پروفایل مشاور',
                              isLoading: state.isSaving,
                              onPressed: state.isSaving ? null : _save,
                            ),
                            if (_canSubmit(profile)) ...[
                              SizedBox(height: r.v(12)),
                              OutlinedButton.icon(
                                onPressed:
                                    state.isSaving ? null : () => _submit(),
                                icon: const Icon(Icons.send_outlined),
                                label: const Text('ارسال برای بررسی'),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  ConsultantProfileInput _input() {
    final experienceText = _experienceController.text.trim();

    return ConsultantProfileInput(
      displayName: _nullableTrim(_displayNameController.text),
      title: _nullableTrim(_titleController.text),
      bio: _nullableTrim(_bioController.text),
      experienceYears:
          experienceText.isEmpty ? null : int.tryParse(experienceText),
      phone: _nullableTrim(_phoneController.text),
      email: _nullableTrim(_emailController.text),
      provinceName: _nullableTrim(_provinceController.text),
      cityName: _nullableTrim(_cityController.text),
      specialtyIds: _selectedSpecialtyIds.toList()..sort(),
    );
  }

  Future<void> _save() async {
    final ok = await ref
        .read(consultantProfileControllerProvider.notifier)
        .save(_input());

    if (!mounted || !ok) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('پروفایل مشاور ذخیره شد.')));
  }

  Future<void> _submit() async {
    final input = _input();

    if ((input.displayName ?? '').length < 2 ||
        (input.title ?? '').length < 2 ||
        (input.bio ?? '').length < 10 ||
        input.specialtyIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'برای ارسال، نام نمایشی، عنوان، توضیحات و حداقل یک تخصص لازم است.',
          ),
        ),
      );
      return;
    }

    final saved = await ref
        .read(consultantProfileControllerProvider.notifier)
        .save(input);
    if (!mounted || !saved) return;

    final submitted =
        await ref.read(consultantProfileControllerProvider.notifier).submit();
    if (!mounted || !submitted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('پروفایل مشاور برای بررسی ارسال شد.')),
    );
  }
}

class _HeaderCard extends StatelessWidget {
  const _HeaderCard({required this.profile});

  final ConsultantProfileModel? profile;

  @override
  Widget build(BuildContext context) {
    final status = profile?.status ?? 'not_created';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(Icons.badge_outlined),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    profile == null
                        ? 'هنوز پروفایل مشاور ندارید'
                        : profile!.resolvedName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                _StatusChip(status: status),
              ],
            ),
            if ((profile?.adminNote ?? '').trim().isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(profile!.adminNote!),
            ],
          ],
        ),
      ),
    );
  }
}

class _SpecialtySelector extends StatelessWidget {
  const _SpecialtySelector({
    required this.specialties,
    required this.selectedIds,
    required this.onToggle,
  });

  final List<ConsultantSpecialtyModel> specialties;
  final Set<int> selectedIds;
  final ValueChanged<int> onToggle;

  @override
  Widget build(BuildContext context) {
    if (specialties.isEmpty) {
      return const Text('تخصصی برای انتخاب وجود ندارد.');
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children:
          specialties.map((specialty) {
            return FilterChip(
              label: Text(specialty.title),
              selected: selectedIds.contains(specialty.id),
              onSelected: (_) => onToggle(specialty.id),
            );
          }).toList(),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final color = switch (status) {
      'approved' => colors.primaryContainer,
      'pending_review' => colors.tertiaryContainer,
      'rejected' => colors.errorContainer,
      'suspended' => colors.errorContainer,
      _ => colors.surfaceContainerHighest,
    };

    return Chip(
      label: Text(_statusLabel(status)),
      backgroundColor: color,
      visualDensity: VisualDensity.compact,
    );
  }
}

class _MessageBox extends StatelessWidget {
  const _MessageBox({required this.message, required this.isError});

  final String message;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: isError ? colors.errorContainer : colors.primaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(
          message,
          style: TextStyle(
            color:
                isError ? colors.onErrorContainer : colors.onPrimaryContainer,
          ),
        ),
      ),
    );
  }
}

bool _canSubmit(ConsultantProfileModel? profile) {
  if (profile == null) return true;
  return profile.status == 'draft' || profile.status == 'rejected';
}

String? _nullableTrim(String value) {
  final clean = value.trim();
  return clean.isEmpty ? null : clean;
}

String _statusLabel(String status) {
  return switch (status) {
    'not_created' => 'ثبت نشده',
    'draft' => 'پیش‌نویس',
    'pending_review' => 'در انتظار بررسی',
    'approved' => 'تأیید شده',
    'rejected' => 'رد شده',
    'suspended' => 'تعلیق شده',
    _ => status,
  };
}
