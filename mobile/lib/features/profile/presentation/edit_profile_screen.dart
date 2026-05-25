import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../../geo/data/geo_models.dart';
import '../data/profile_models.dart';
import '../state/profile_controller.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _displayNameController = TextEditingController();
  final _nationalIdController = TextEditingController();
  final _birthDateController = TextEditingController(text: '1995-01-01');
  final _addressController = TextEditingController();
  final _postalCodeController = TextEditingController();
  final _bioController = TextEditingController();

  String? _gender = 'male';
  int? _provinceId;
  int? _countyId;
  int? _cityId;
  bool _filled = false;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _displayNameController.dispose();
    _nationalIdController.dispose();
    _birthDateController.dispose();
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
    _birthDateController.text = profile.birthDate ?? '1995-01-01';
    _addressController.text = profile.address ?? '';
    _postalCodeController.text = profile.postalCode ?? '';
    _bioController.text = profile.bio ?? '';

    _gender = profile.gender ?? 'male';
    _provinceId = profile.provinceId;
    _countyId = profile.countyId;
    _cityId = profile.cityId;
  }

  Future<void> _save() async {
    final input = ProfileUpdateInput(
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      displayName: _displayNameController.text.trim(),
      nationalId: _nationalIdController.text.trim(),
      birthDate: _birthDateController.text.trim(),
      gender: _gender,
      provinceId: _provinceId,
      countyId: _countyId,
      cityId: _cityId,
      address: _addressController.text.trim(),
      postalCode: _postalCodeController.text.trim(),
      bio: _bioController.text.trim(),
    );

    final ok = await ref.read(profileControllerProvider.notifier).update(input);

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileControllerProvider);
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
      appBar: AppBar(
        title: const Text('ویرایش پروفایل'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          if (state.isLoading) {
            return const FarmLoadingView();
          }

          return SingleChildScrollView(
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(r.s(20)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        FarmTextField(
                          controller: _firstNameController,
                          label: 'نام',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _lastNameController,
                          label: 'نام خانوادگی',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _displayNameController,
                          label: 'نام نمایشی',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _nationalIdController,
                          label: 'کد ملی',
                          keyboardType: TextInputType.number,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _birthDateController,
                          label: 'تاریخ تولد میلادی فعلاً',
                          keyboardType: TextInputType.datetime,
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<String>(
                          initialValue: _gender,
                          decoration: const InputDecoration(
                            labelText: 'جنسیت',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(value: 'male', child: Text('مرد')),
                            DropdownMenuItem(
                              value: 'female',
                              child: Text('زن'),
                            ),
                            DropdownMenuItem(
                              value: 'other',
                              child: Text('سایر'),
                            ),
                          ],
                          onChanged: (value) {
                            setState(() => _gender = value);
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          initialValue: selectedProvinceId,
                          decoration: const InputDecoration(
                            labelText: 'استان',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              state.provinces
                                  .map(
                                    (item) => DropdownMenuItem<int>(
                                      value: item.id,
                                      child: Text(item.name),
                                    ),
                                  )
                                  .toList(),
                          onChanged: (value) async {
                            setState(() {
                              _provinceId = value;
                              _countyId = null;
                              _cityId = null;
                            });

                            if (value != null) {
                              await ref
                                  .read(profileControllerProvider.notifier)
                                  .loadCounties(value);
                            }
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          initialValue: selectedCountyId,
                          decoration: const InputDecoration(
                            labelText: 'شهرستان',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              state.counties
                                  .map(
                                    (item) => DropdownMenuItem<int>(
                                      value: item.id,
                                      child: Text(item.name),
                                    ),
                                  )
                                  .toList(),
                          onChanged: (value) async {
                            setState(() {
                              _countyId = value;
                              _cityId = null;
                            });

                            await ref
                                .read(profileControllerProvider.notifier)
                                .loadCities(
                                  provinceId: _provinceId,
                                  countyId: value,
                                );
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          initialValue: selectedCityId,
                          decoration: const InputDecoration(
                            labelText: 'شهر',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              state.cities
                                  .map(
                                    (GeoCity item) => DropdownMenuItem<int>(
                                      value: item.id,
                                      child: Text(item.name),
                                    ),
                                  )
                                  .toList(),
                          onChanged: (value) {
                            setState(() => _cityId = value);
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _addressController,
                          label: 'آدرس',
                          maxLines: 3,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _postalCodeController,
                          label: 'کد پستی',
                          keyboardType: TextInputType.number,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _bioController,
                          label: 'بیوگرافی',
                          maxLines: 3,
                        ),
                        if (state.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        FarmButton(
                          label: 'ذخیره پروفایل',
                          isLoading: state.isSaving,
                          onPressed: state.isSaving ? null : _save,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
