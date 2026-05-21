import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../../geo/data/geo_models.dart';
import '../../media/presentation/media_upload_button.dart';
import '../../profile/state/profile_controller.dart';
import '../data/store_models.dart';
import '../state/store_controller.dart';

class EditStoreScreen extends ConsumerStatefulWidget {
  const EditStoreScreen({required this.store, super.key});

  final Store? store;

  @override
  ConsumerState<EditStoreScreen> createState() => _EditStoreScreenState();
}

class _EditStoreScreenState extends ConsumerState<EditStoreScreen> {
  final _nameController = TextEditingController();
  final _slugController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _phoneController = TextEditingController(text: '989120000000');
  final _emailController = TextEditingController(text: 'store@example.com');
  final _addressController = TextEditingController();
  final _postalCodeController = TextEditingController(text: '1234567890');

  String _storeType = 'mixed';
  int? _provinceId;
  int? _countyId;
  int? _cityId;
  String? _logoMediaFileKey;
  String? _bannerMediaFileKey;

  bool _filled = false;
  bool _geoLoaded = false;

  @override
  void dispose() {
    _nameController.dispose();
    _slugController.dispose();
    _descriptionController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _addressController.dispose();
    _postalCodeController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_geoLoaded) return;
    _geoLoaded = true;

    final store = widget.store;
    if (store == null) return;

    Future.microtask(() async {
      final profileController = ref.read(profileControllerProvider.notifier);

      if (store.provinceId != null) {
        await profileController.loadCounties(store.provinceId!);
      }

      if (store.countyId != null) {
        await profileController.loadCities(
          provinceId: store.provinceId,
          countyId: store.countyId,
        );
      }
    });
  }

  void _fillOnce(Store? store) {
    if (_filled) return;
    _filled = true;

    if (store == null) {
      _nameController.text = 'فروشگاه فارم نت';
      _slugController.text =
          'farmnet-store-${DateTime.now().millisecondsSinceEpoch}';
      _descriptionController.text = 'فروشگاه تستی فارم نت';
      _addressController.text = 'آدرس تست فروشگاه';
      return;
    }

    _nameController.text = store.name;
    _slugController.text = store.slug;
    _descriptionController.text = store.description ?? '';
    _phoneController.text = store.phone ?? '';
    _emailController.text = store.email ?? '';
    _addressController.text = store.address ?? '';
    _postalCodeController.text = store.postalCode ?? '';
    _storeType = store.storeType;
    _provinceId = store.provinceId;
    _countyId = store.countyId;
    _cityId = store.cityId;
    _logoMediaFileKey = store.logoFileKey;
    _bannerMediaFileKey = store.bannerFileKey;
  }

  Future<void> _save() async {
    final store = widget.store;
    final controller = ref.read(storeControllerProvider.notifier);

    final ok =
        store == null
            ? await controller.createStore(
              StoreCreateInput(
                name: _nameController.text.trim(),
                slug: _slugController.text.trim(),
                description: _descriptionController.text.trim(),
                storeType: _storeType,
                phone: _phoneController.text.trim(),
                email: _emailController.text.trim(),
                provinceId: _provinceId,
                countyId: _countyId,
                cityId: _cityId,
                address: _addressController.text.trim(),
                postalCode: _postalCodeController.text.trim(),
                logoMediaFileKey: _logoMediaFileKey,
                bannerMediaFileKey: _bannerMediaFileKey,
              ),
            )
            : await controller.updateStore(
              storeId: store.id,
              input: StoreUpdateInput(
                name: _nameController.text.trim(),
                slug: _slugController.text.trim(),
                description: _descriptionController.text.trim(),
                storeType: _storeType,
                phone: _phoneController.text.trim(),
                email: _emailController.text.trim(),
                provinceId: _provinceId,
                countyId: _countyId,
                cityId: _cityId,
                address: _addressController.text.trim(),
                postalCode: _postalCodeController.text.trim(),
                logoMediaFileKey: _logoMediaFileKey,
                bannerMediaFileKey: _bannerMediaFileKey,
              ),
            );

    if (!ok || !mounted) return;

    if (store == null &&
        (_logoMediaFileKey != null || _bannerMediaFileKey != null)) {
      final createdStore = ref.read(storeControllerProvider).myStore;
      if (createdStore != null) {
        final mediaOk = await controller.updateStore(
          storeId: createdStore.id,
          input: StoreUpdateInput(
            logoMediaFileKey: _logoMediaFileKey,
            bannerMediaFileKey: _bannerMediaFileKey,
          ),
        );

        if (!mediaOk || !mounted) return;
      }
    }

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final storeState = ref.watch(storeControllerProvider);
    final profileState = ref.watch(profileControllerProvider);
    final profileController = ref.read(profileControllerProvider.notifier);

    _fillOnce(widget.store);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.store == null ? 'ساخت فروشگاه' : 'ویرایش فروشگاه'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
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
                          controller: _nameController,
                          label: 'نام فروشگاه',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _slugController,
                          label: 'Slug انگلیسی',
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<String>(
                          value: _storeType,
                          decoration: const InputDecoration(
                            labelText: 'نوع فروشگاه',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'agriculture_inputs',
                              child: Text('نهاده‌های کشاورزی'),
                            ),
                            DropdownMenuItem(
                              value: 'equipment',
                              child: Text('تجهیزات'),
                            ),
                            DropdownMenuItem(
                              value: 'seeds',
                              child: Text('بذر'),
                            ),
                            DropdownMenuItem(
                              value: 'fertilizer',
                              child: Text('کود'),
                            ),
                            DropdownMenuItem(
                              value: 'pesticide',
                              child: Text('سموم'),
                            ),
                            DropdownMenuItem(
                              value: 'mixed',
                              child: Text('چندمنظوره'),
                            ),
                            DropdownMenuItem(
                              value: 'other',
                              child: Text('سایر'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _storeType = value);
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _descriptionController,
                          label: 'توضیحات',
                          maxLines: 3,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _phoneController,
                          label: 'تلفن',
                          keyboardType: TextInputType.phone,
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _emailController,
                          label: 'ایمیل',
                          keyboardType: TextInputType.emailAddress,
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          value: _provinceId,
                          decoration: const InputDecoration(
                            labelText: 'استان',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              profileState.provinces
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
                              await profileController.loadCounties(value);
                            }
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          value: _countyId,
                          decoration: const InputDecoration(
                            labelText: 'شهرستان',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              profileState.counties
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

                            await profileController.loadCities(
                              provinceId: _provinceId,
                              countyId: value,
                            );
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<int>(
                          value: _cityId,
                          decoration: const InputDecoration(
                            labelText: 'شهر',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              profileState.cities
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
                        SizedBox(height: r.v(16)),
                        MediaUploadButton(
                          label: 'آپلود لوگوی فروشگاه',
                          purpose: 'store_logo',
                          visibility: 'public',
                          allowedExtensions: const [
                            'jpg',
                            'jpeg',
                            'png',
                            'webp',
                          ],
                          onUploaded: (media) {
                            setState(() {
                              _logoMediaFileKey = media.fileKey;
                            });
                          },
                        ),
                        if (_logoMediaFileKey != null) ...[
                          SizedBox(height: r.v(8)),
                          Text('لوگو آپلود شد: $_logoMediaFileKey'),
                        ],
                        SizedBox(height: r.v(12)),
                        MediaUploadButton(
                          label: 'آپلود بنر فروشگاه',
                          purpose: 'store_banner',
                          visibility: 'public',
                          allowedExtensions: const [
                            'jpg',
                            'jpeg',
                            'png',
                            'webp',
                          ],
                          onUploaded: (media) {
                            setState(() {
                              _bannerMediaFileKey = media.fileKey;
                            });
                          },
                        ),
                        if (_bannerMediaFileKey != null) ...[
                          SizedBox(height: r.v(8)),
                          Text('بنر آپلود شد: $_bannerMediaFileKey'),
                        ],
                        if (storeState.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            storeState.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        FarmButton(
                          label: 'ذخیره فروشگاه',
                          isLoading: storeState.isSaving,
                          onPressed: storeState.isSaving ? null : _save,
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
