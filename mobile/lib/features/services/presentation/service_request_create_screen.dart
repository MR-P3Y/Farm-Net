import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/dates.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../geo/data/geo_models.dart';
import '../../geo/data/geo_repository.dart';
import '../data/service_models.dart';
import '../state/service_discovery_controller.dart';
import '../state/service_request_controller.dart';
import 'service_ui.dart';

final _provincesProvider = FutureProvider(
  (ref) => ref.watch(geoRepositoryProvider).getProvinces(),
);
final _citiesProvider = FutureProvider.family<List<GeoCity>, int>(
  (ref, provinceId) =>
      ref.watch(geoRepositoryProvider).getCities(provinceId: provinceId),
);

class ServiceRequestCreateScreen extends ConsumerStatefulWidget {
  const ServiceRequestCreateScreen({required this.offerId, super.key});
  final int offerId;
  @override
  ConsumerState<ServiceRequestCreateScreen> createState() =>
      _ServiceRequestCreateScreenState();
}

class _ServiceRequestCreateScreenState
    extends ConsumerState<ServiceRequestCreateScreen> {
  final _title = TextEditingController();
  final _description = TextEditingController();
  final _budget = TextEditingController();
  final _address = TextEditingController();
  String _contactMethod = 'in_app';
  int? _provinceId;
  int? _cityId;
  DateTime? _scheduledAt;

  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    _budget.dispose();
    _address.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final offerAsync = ref.watch(serviceOfferDetailProvider(widget.offerId));
    final requestState = ref.watch(serviceRequestControllerProvider);
    final provinces =
        ref.watch(_provincesProvider).valueOrNull ?? const <GeoProvince>[];
    final cities =
        _provinceId == null
            ? const <GeoCity>[]
            : (ref.watch(_citiesProvider(_provinceId!)).valueOrNull ??
                const <GeoCity>[]);
    return Scaffold(
      appBar: FarmAppBar(
        title: context.l10n.tr(fa: 'درخواست خدمت', en: 'Service request'),
        fallbackLocation: '/services/${widget.offerId}',
      ),
      body: ResponsiveBuilder(
        builder:
            (context, constraints, r) => offerAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error:
                  (_, __) => Center(
                    child: Text(
                      context.l10n.tr(
                        fa: 'دریافت اطلاعات خدمت ناموفق بود.',
                        en: 'Could not load service information.',
                      ),
                    ),
                  ),
              data:
                  (offer) => ListView(
                    padding: r.pagePadding(),
                    children: [
                      Card(
                        child: ListTile(
                          leading: const Icon(Icons.agriculture_outlined),
                          title: Text(offer.title),
                          subtitle: Text(
                            serviceProviderName(context, offer.provider),
                          ),
                        ),
                      ),
                      SizedBox(height: r.v(12)),
                      TextField(
                        controller: _title,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'عنوان درخواست',
                            en: 'Request title',
                          ),
                        ),
                      ),
                      SizedBox(height: r.v(12)),
                      TextField(
                        controller: _description,
                        minLines: 4,
                        maxLines: 8,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'شرح نیاز',
                            en: 'Describe your need',
                          ),
                        ),
                      ),
                      SizedBox(height: r.v(12)),
                      DropdownButtonFormField<String>(
                        initialValue: _contactMethod,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'روش ارتباط',
                            en: 'Contact method',
                          ),
                        ),
                        items: [
                          DropdownMenuItem(
                            value: 'in_app',
                            child: Text(
                              context.l10n.tr(
                                fa: 'داخل اپلیکیشن',
                                en: 'In app',
                              ),
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'phone',
                            child: Text(
                              context.l10n.tr(
                                fa: 'تماس تلفنی',
                                en: 'Phone call',
                              ),
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'video',
                            child: Text(
                              context.l10n.tr(
                                fa: 'تماس تصویری',
                                en: 'Video call',
                              ),
                            ),
                          ),
                          DropdownMenuItem(
                            value: 'visit',
                            child: Text(
                              context.l10n.tr(
                                fa: 'بازدید حضوری',
                                en: 'On-site visit',
                              ),
                            ),
                          ),
                        ],
                        onChanged:
                            (value) => setState(
                              () => _contactMethod = value ?? 'in_app',
                            ),
                      ),
                      SizedBox(height: r.v(12)),
                      TextField(
                        controller: _budget,
                        keyboardType: TextInputType.number,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'بودجه پیشنهادی (تومان) — اختیاری',
                            en: 'Suggested budget (Toman) — optional',
                          ),
                        ),
                      ),
                      SizedBox(height: r.v(12)),
                      DropdownButtonFormField<int?>(
                        initialValue: _provinceId,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'استان — اختیاری',
                            en: 'Province — optional',
                          ),
                        ),
                        items: [
                          DropdownMenuItem(
                            value: null,
                            child: Text(
                              context.l10n.tr(
                                fa: 'انتخاب نشده',
                                en: 'Not selected',
                              ),
                            ),
                          ),
                          ...provinces.map(
                            (item) => DropdownMenuItem(
                              value: item.id,
                              child: Text(item.name),
                            ),
                          ),
                        ],
                        onChanged:
                            (value) => setState(() {
                              _provinceId = value;
                              _cityId = null;
                            }),
                      ),
                      SizedBox(height: r.v(12)),
                      DropdownButtonFormField<int?>(
                        initialValue: _cityId,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'شهر — اختیاری',
                            en: 'City — optional',
                          ),
                        ),
                        items: [
                          DropdownMenuItem(
                            value: null,
                            child: Text(
                              context.l10n.tr(
                                fa: 'انتخاب نشده',
                                en: 'Not selected',
                              ),
                            ),
                          ),
                          ...cities.map(
                            (item) => DropdownMenuItem(
                              value: item.id,
                              child: Text(item.name),
                            ),
                          ),
                        ],
                        onChanged: (value) => setState(() => _cityId = value),
                      ),
                      SizedBox(height: r.v(12)),
                      TextField(
                        controller: _address,
                        minLines: 2,
                        maxLines: 4,
                        decoration: InputDecoration(
                          labelText: context.l10n.tr(
                            fa: 'نشانی محل خدمت — اختیاری',
                            en: 'Service address — optional',
                          ),
                        ),
                      ),
                      SizedBox(height: r.v(12)),
                      OutlinedButton.icon(
                        onPressed: _pickDate,
                        icon: const Icon(Icons.event_outlined),
                        label: Text(
                          _scheduledAt == null
                              ? context.l10n.tr(
                                fa: 'انتخاب زمان پیشنهادی',
                                en: 'Choose a preferred date',
                              )
                              : _scheduledAt!.format(context),
                        ),
                      ),
                      if (requestState.errorMessage != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 12),
                          child: Text(
                            requestState.errorMessage!,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ),
                      SizedBox(height: r.v(16)),
                      FilledButton.icon(
                        onPressed:
                            requestState.isSaving
                                ? null
                                : () => _submit(offer, provinces, cities),
                        icon: const Icon(Icons.send_outlined),
                        label: Text(
                          context.l10n.tr(
                            fa: 'ثبت درخواست',
                            en: 'Submit request',
                          ),
                        ),
                      ),
                    ],
                  ),
            ),
      ),
    );
  }

  Future<void> _pickDate() async {
    final value = await showLocalizedDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (value != null) setState(() => _scheduledAt = value);
  }

  Future<void> _submit(
    ServiceOffer offer,
    List<GeoProvince> provinces,
    List<GeoCity> cities,
  ) async {
    if (_title.text.trim().length < 2 || _description.text.trim().length < 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'عنوان و شرح درخواست را کامل کنید.',
              en: 'Complete the request title and description.',
            ),
          ),
        ),
      );
      return;
    }
    final province =
        provinces.where((item) => item.id == _provinceId).firstOrNull;
    final city = cities.where((item) => item.id == _cityId).firstOrNull;
    final created = await ref
        .read(serviceRequestControllerProvider.notifier)
        .create(
          ServiceRequestInput(
            offerId: offer.id,
            title: _title.text.trim(),
            description: _description.text.trim(),
            contactMethod: _contactMethod,
            budgetAmount: double.tryParse(_budget.text.trim()),
            scheduledAt: _scheduledAt?.toIso8601String(),
            provinceId: _provinceId,
            cityId: _cityId,
            provinceName: province?.name,
            cityName: city?.name,
            addressText: _address.text,
          ),
        );
    if (created != null && mounted) {
      context.pushReplacement('/services/requests/${created.id}');
    }
  }
}
