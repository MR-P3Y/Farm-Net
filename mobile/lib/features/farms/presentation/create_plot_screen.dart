import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../data/farm_models.dart';
import '../data/farm_repository.dart';
import '../domain/plot_geometry.dart';
import 'widgets/farm_location_search_sheet.dart';
import 'widgets/farm_map_layers.dart';

class CreatePlotScreen extends ConsumerStatefulWidget {
  const CreatePlotScreen({
    required this.farmId,
    required this.farmName,
    this.initialCenter,
    super.key,
  });

  final int farmId;
  final String farmName;
  final LatLng? initialCenter;

  @override
  ConsumerState<CreatePlotScreen> createState() => _CreatePlotScreenState();
}

class _CreatePlotScreenState extends ConsumerState<CreatePlotScreen> {
  static const _iranCenter = LatLng(32.4279, 53.6880);

  final _mapController = MapController();
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _areaController = TextEditingController();
  final List<LatLng> _vertices = [];

  late LatLng _selectedCenter;
  var _step = 0;
  var _locationChosen = false;
  var _locating = false;
  var _submitting = false;
  var _mapReady = false;
  var _mapStyle = FarmMapStyle.satellite;
  var _resolvingLocation = false;
  FarmLocationResult? _selectedPlace;

  @override
  void initState() {
    super.initState();
    _selectedCenter = widget.initialCenter ?? _iranCenter;
    _locationChosen = widget.initialCenter != null;
  }

  @override
  void dispose() {
    _mapController.dispose();
    _nameController.dispose();
    _descriptionController.dispose();
    _areaController.dispose();
    super.dispose();
  }

  double get _boundaryArea => PlotGeometry.areaSquareMetres(_vertices);

  bool get _boundaryIsValid =>
      _vertices.length >= 3 &&
      _vertices.length <= 499 &&
      !PlotGeometry.hasSelfIntersection(_vertices);

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: FarmAppBar(title: l10n.tr(fa: 'افزودن قطعه', en: 'Add plot')),
      body: Column(
        children: [
          _StepHeader(current: _step),
          Expanded(
            child:
                _step == 2
                    ? _buildDetails(l10n)
                    : _buildMap(l10n, drawing: _step == 1),
          ),
          _buildBottomActions(l10n),
        ],
      ),
    );
  }

  Widget _buildMap(AppLocalizations l10n, {required bool drawing}) {
    final selfIntersecting = PlotGeometry.hasSelfIntersection(_vertices);
    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: _selectedCenter,
            initialZoom: widget.initialCenter == null ? 5.2 : 15,
            minZoom: 4,
            maxZoom: 19,
            onMapReady: () => _mapReady = true,
            onPositionChanged: (camera, hasGesture) {
              if (!drawing && hasGesture) {
                _selectedCenter = camera.center;
                if (mounted && (!_locationChosen || _selectedPlace != null)) {
                  setState(() {
                    _locationChosen = true;
                    _selectedPlace = null;
                  });
                }
              }
            },
            onTap:
                drawing
                    ? (_, point) {
                      if (_vertices.length >= 499) return;
                      setState(() => _vertices.add(point));
                    }
                    : null,
          ),
          children: [
            FarmMapTiles(style: _mapStyle),
            if (_vertices.length >= 2)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: _vertices,
                    color:
                        selfIntersecting
                            ? Theme.of(context).colorScheme.error
                            : const Color(0xFF0F4D2E),
                    strokeWidth: 4,
                  ),
                ],
              ),
            if (_vertices.length >= 3)
              PolygonLayer(
                polygons: [
                  Polygon(
                    points: _vertices,
                    color: (selfIntersecting
                            ? Theme.of(context).colorScheme.error
                            : const Color(0xFF2E7D32))
                        .withValues(alpha: 0.24),
                    borderColor:
                        selfIntersecting
                            ? Theme.of(context).colorScheme.error
                            : const Color(0xFF0F4D2E),
                    borderStrokeWidth: 3,
                  ),
                ],
              ),
            if (drawing)
              MarkerLayer(
                markers: [
                  for (var index = 0; index < _vertices.length; index++)
                    Marker(
                      point: _vertices[index],
                      width: 38,
                      height: 38,
                      child: GestureDetector(
                        key: ValueKey('boundary-point-$index'),
                        onTap: () => setState(() => _vertices.removeAt(index)),
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            color: const Color(0xFF0F4D2E),
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 3),
                            boxShadow: const [
                              BoxShadow(color: Colors.black26, blurRadius: 5),
                            ],
                          ),
                          child: Center(
                            child: Text(
                              '${index + 1}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            FarmMapAttribution(
              style: _mapStyle,
              bottomPadding: drawing ? 82 : 6,
            ),
          ],
        ),
        if (!drawing)
          const IgnorePointer(
            child: Center(
              child: Padding(
                padding: EdgeInsets.only(bottom: 42),
                child: Icon(
                  Icons.location_pin,
                  color: Color(0xFF0F4D2E),
                  size: 58,
                  shadows: [Shadow(color: Colors.black38, blurRadius: 8)],
                ),
              ),
            ),
          ),
        PositionedDirectional(
          top: 14,
          start: 14,
          end: 14,
          child: FarmGlassCard(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Icon(
                      drawing ? Icons.gesture_rounded : Icons.map_rounded,
                      color: const Color(0xFF0F4D2E),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        drawing
                            ? l10n.tr(
                              fa: 'گوشه‌های زمین را به‌ترتیب لمس کنید.',
                              en: 'Tap the plot corners in order.',
                            )
                            : l10n.tr(
                              fa:
                                  'نقشه را جابه‌جا کنید تا نشانگر روی زمین قرار بگیرد.',
                              en: 'Move the map until the pin is over the plot.',
                            ),
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    FarmMapLayerToggle(
                      value: _mapStyle,
                      onChanged: (value) => setState(() => _mapStyle = value),
                    ),
                    if (!drawing) ...[
                      const SizedBox(width: 8),
                      IconButton.filledTonal(
                        key: const ValueKey('farm-location-search-open'),
                        tooltip: l10n.tr(
                          fa: 'جست‌وجوی شهر یا روستا',
                          en: 'Search city or village',
                        ),
                        onPressed: _openLocationSearch,
                        icon: const Icon(Icons.travel_explore_rounded),
                      ),
                    ],
                  ],
                ),
                if (!drawing && _selectedPlace != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    _selectedPlace!.displayName,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        PositionedDirectional(
          end: 14,
          bottom: drawing ? 90 : 24,
          child: Column(
            children: [
              FloatingActionButton.small(
                heroTag: 'plot-map-zoom-in',
                onPressed:
                    () => _mapController.move(
                      _mapController.camera.center,
                      _mapController.camera.zoom + 1,
                    ),
                child: const Icon(Icons.add),
              ),
              const SizedBox(height: 8),
              FloatingActionButton.small(
                heroTag: 'plot-map-zoom-out',
                onPressed:
                    () => _mapController.move(
                      _mapController.camera.center,
                      _mapController.camera.zoom - 1,
                    ),
                child: const Icon(Icons.remove),
              ),
              if (!drawing) ...[
                const SizedBox(height: 8),
                FloatingActionButton(
                  heroTag: 'plot-current-location',
                  onPressed: _locating ? null : _useCurrentLocation,
                  child:
                      _locating
                          ? const Padding(
                            padding: EdgeInsets.all(15),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                          : const Icon(Icons.my_location_rounded),
                ),
              ],
            ],
          ),
        ),
        if (drawing)
          PositionedDirectional(
            start: 14,
            end: 14,
            bottom: 16,
            child: Row(
              children: [
                Expanded(
                  child: _MapStatusChip(
                    icon: Icons.square_foot_rounded,
                    label:
                        _vertices.length < 3
                            ? l10n.tr(
                              fa: '${_vertices.length} نقطه ثبت شده',
                              en: '${_vertices.length} points added',
                            )
                            : _formatArea(_boundaryArea, l10n),
                    error: selfIntersecting,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filledTonal(
                  tooltip: l10n.tr(fa: 'حذف آخرین نقطه', en: 'Undo last point'),
                  onPressed:
                      _vertices.isEmpty
                          ? null
                          : () => setState(() => _vertices.removeLast()),
                  icon: const Icon(Icons.undo_rounded),
                ),
                const SizedBox(width: 6),
                IconButton.filledTonal(
                  tooltip: l10n.tr(fa: 'پاک‌کردن مرز', en: 'Clear boundary'),
                  onPressed:
                      _vertices.isEmpty
                          ? null
                          : () => setState(_vertices.clear),
                  icon: const Icon(Icons.delete_outline_rounded),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildDetails(AppLocalizations l10n) {
    final hasBoundary = _vertices.length >= 3;
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            FarmGlassCard(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  const CircleAvatar(
                    backgroundColor: Color(0xFFE3F2E4),
                    child: Icon(Icons.check_rounded, color: Color(0xFF0F4D2E)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.tr(
                            fa: 'موقعیت قطعه انتخاب شد',
                            en: 'Plot location selected',
                          ),
                          style: const TextStyle(fontWeight: FontWeight.w900),
                        ),
                        Text(
                          hasBoundary
                              ? l10n.tr(
                                fa: 'مرز و مساحت قطعه نیز ثبت شده است.',
                                en: 'The boundary and area are also captured.',
                              )
                              : l10n.tr(
                                fa: 'فقط نقطهٔ مرکزی ثبت می‌شود.',
                                en: 'Only the center point will be saved.',
                              ),
                        ),
                        if (_selectedPlace != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            _selectedPlace!.displayName,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            TextFormField(
              controller: _nameController,
              textInputAction: TextInputAction.next,
              decoration: InputDecoration(
                labelText: l10n.tr(fa: 'نام قطعه *', en: 'Plot name *'),
                prefixIcon: const Icon(Icons.landscape_outlined),
              ),
              validator:
                  (value) =>
                      value == null || value.trim().isEmpty
                          ? l10n.tr(
                            fa: 'نام قطعه را وارد کنید.',
                            en: 'Enter a plot name.',
                          )
                          : null,
            ),
            const SizedBox(height: 14),
            TextFormField(
              controller: _descriptionController,
              minLines: 2,
              maxLines: 4,
              decoration: InputDecoration(
                labelText: l10n.tr(
                  fa: 'توضیحات (اختیاری)',
                  en: 'Description (optional)',
                ),
                prefixIcon: const Icon(Icons.notes_rounded),
              ),
            ),
            const SizedBox(height: 14),
            if (hasBoundary)
              InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.tr(
                    fa: 'مساحت محاسبه‌شده',
                    en: 'Calculated area',
                  ),
                  prefixIcon: const Icon(Icons.square_foot_rounded),
                ),
                child: Text(
                  _formatArea(_boundaryArea, l10n),
                  style: const TextStyle(fontWeight: FontWeight.w900),
                ),
              )
            else
              TextFormField(
                controller: _areaController,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: InputDecoration(
                  labelText: l10n.tr(
                    fa: 'مساحت تقریبی (متر مربع) *',
                    en: 'Approximate area (m²) *',
                  ),
                  prefixIcon: const Icon(Icons.square_foot_rounded),
                ),
                validator: (value) {
                  final area = double.tryParse(value ?? '');
                  if (area == null || area <= 0) {
                    return l10n.tr(
                      fa: 'مساحت معتبر وارد کنید.',
                      en: 'Enter a valid area.',
                    );
                  }
                  return null;
                },
              ),
            const SizedBox(height: 12),
            Text(
              l10n.tr(
                fa:
                    'مختصات در پشت‌صحنه ذخیره می‌شود و نیازی به واردکردن طول یا عرض جغرافیایی نیست.',
                en:
                    'Coordinates are saved in the background; latitude and longitude never need manual entry.',
              ),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomActions(AppLocalizations l10n) {
    final canContinue =
        _step == 0
            ? _locationChosen && !_resolvingLocation
            : _step == 1
            ? _vertices.isEmpty || _boundaryIsValid
            : !_submitting;
    return SafeArea(
      top: false,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          border: Border(
            top: BorderSide(color: Theme.of(context).dividerColor),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
          child: Row(
            children: [
              if (_step > 0) ...[
                OutlinedButton.icon(
                  onPressed: _submitting ? null : _back,
                  icon: const Icon(Icons.arrow_forward_rounded),
                  label: Text(l10n.tr(fa: 'قبلی', en: 'Back')),
                ),
                const SizedBox(width: 10),
              ],
              Expanded(
                child: FilledButton.icon(
                  key: const ValueKey('plot-next-action'),
                  onPressed:
                      canContinue ? (_step == 2 ? _submit : _next) : null,
                  icon:
                      _submitting || _resolvingLocation
                          ? const SizedBox.square(
                            dimension: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                          : Icon(
                            _step == 2
                                ? Icons.check_rounded
                                : Icons.arrow_back_rounded,
                          ),
                  label: Text(
                    _step == 2
                        ? l10n.tr(fa: 'ثبت قطعه', en: 'Save plot')
                        : _step == 1 && _vertices.isEmpty
                        ? l10n.tr(
                          fa: 'ادامه فقط با نقطه',
                          en: 'Continue with point only',
                        )
                        : l10n.tr(fa: 'ادامه', en: 'Continue'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _next() async {
    if (_step == 0) {
      await _resolveSelectedLocation();
      if (!mounted) return;
      setState(() => _step = 1);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_mapReady) _mapController.move(_selectedCenter, 16);
      });
      return;
    }
    if (_step == 1) {
      if (_vertices.isNotEmpty && !_boundaryIsValid) return;
      if (_vertices.length >= 3) {
        _selectedCenter = PlotGeometry.center(
          _vertices,
          fallback: _selectedCenter,
        );
        _areaController.text = _boundaryArea.toStringAsFixed(2);
      }
      setState(() => _step = 2);
    }
  }

  void _back() {
    setState(() => _step--);
    if (_step < 2) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_mapReady) _mapController.move(_selectedCenter, 16);
      });
    }
  }

  Future<void> _useCurrentLocation() async {
    final l10n = context.l10n;
    setState(() => _locating = true);
    try {
      if (!await Geolocator.isLocationServiceEnabled()) {
        throw _LocationFailure(
          l10n.tr(
            fa: 'سرویس موقعیت مکانی دستگاه خاموش است.',
            en: 'Location services are disabled.',
          ),
        );
      }
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw _LocationFailure(
          l10n.tr(
            fa: 'اجازهٔ دسترسی به موقعیت داده نشد.',
            en: 'Location permission was not granted.',
          ),
        );
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
        ),
      );
      if (!mounted) return;
      final point = LatLng(position.latitude, position.longitude);
      setState(() {
        _selectedCenter = point;
        _locationChosen = true;
        _selectedPlace = null;
      });
      _mapController.move(point, 17);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            error is _LocationFailure
                ? error.message
                : l10n.tr(
                  fa: 'موقعیت فعلی دریافت نشد؛ محل را روی نقشه انتخاب کنید.',
                  en: 'Current location could not be read; select it on the map.',
                ),
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _locating = false);
    }
  }

  Future<void> _openLocationSearch() async {
    final language = context.l10n.isFa ? 'fa' : 'en';
    final result = await showFarmLocationSearchSheet(
      context,
      onSearch:
          (query) => ref
              .read(farmRepositoryProvider)
              .searchLocations(query: query, language: language),
    );
    if (!mounted || result == null) return;
    final point = LatLng(result.latitude, result.longitude);
    setState(() {
      _selectedCenter = point;
      _selectedPlace = result;
      _locationChosen = true;
    });
    _mapController.move(point, 15.5);
  }

  Future<void> _resolveSelectedLocation() async {
    if (_selectedPlace != null || !_locationChosen) return;
    final l10n = context.l10n;
    setState(() => _resolvingLocation = true);
    try {
      final result = await ref
          .read(farmRepositoryProvider)
          .reverseLocation(
            latitude: _selectedCenter.latitude,
            longitude: _selectedCenter.longitude,
            language: l10n.isFa ? 'fa' : 'en',
          );
      if (mounted) setState(() => _selectedPlace = result);
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            l10n.tr(
              fa: 'نام مکان پیدا نشد؛ مختصات انتخاب‌شده همچنان ذخیره می‌شود.',
              en:
                  'No place name was found; the selected coordinates will still be saved.',
            ),
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _resolvingLocation = false);
    }
  }

  Future<void> _submit() async {
    if (_formKey.currentState?.validate() != true) return;
    final l10n = context.l10n;
    final area =
        _vertices.length >= 3
            ? _boundaryArea
            : double.parse(_areaController.text);
    final center = PlotGeometry.center(_vertices, fallback: _selectedCenter);
    setState(() => _submitting = true);
    try {
      final payload = <String, dynamic>{
        'name': _nameController.text.trim(),
        'description':
            _descriptionController.text.trim().isEmpty
                ? null
                : _descriptionController.text.trim(),
        'area_sqm': double.parse(area.toStringAsFixed(2)),
        'latitude': double.parse(center.latitude.toStringAsFixed(7)),
        'longitude': double.parse(center.longitude.toStringAsFixed(7)),
        'boundary':
            _vertices.length >= 3
                ? PlotGeometry.closedBoundaryPayload(_vertices)
                : null,
        ...?_selectedPlace?.geoPayload,
      };
      final created = await ref
          .read(farmRepositoryProvider)
          .createPlot(widget.farmId, payload);
      if (mounted) Navigator.pop(context, created);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            l10n.tr(
              fa: 'ثبت قطعه انجام نشد: $error',
              en: 'The plot could not be saved: $error',
            ),
          ),
        ),
      );
      setState(() => _submitting = false);
    }
  }

  static String _formatArea(double area, AppLocalizations l10n) {
    final raw =
        area >= 10000
            ? (area / 10000).toStringAsFixed(2)
            : area.toStringAsFixed(0);
    final number = l10n.isFa ? toPersianDigits(raw) : raw;
    if (area >= 10000) {
      return l10n.tr(fa: '$number هکتار', en: '$number ha');
    }
    return l10n.tr(fa: '$number متر مربع', en: '$number m²');
  }
}

class _StepHeader extends StatelessWidget {
  const _StepHeader({required this.current});

  final int current;

  @override
  Widget build(BuildContext context) {
    final labels = [
      context.l10n.tr(fa: 'موقعیت', en: 'Location'),
      context.l10n.tr(fa: 'مرز زمین', en: 'Boundary'),
      context.l10n.tr(fa: 'اطلاعات', en: 'Details'),
    ];
    return Padding(
      padding: const EdgeInsets.fromLTRB(18, 10, 18, 12),
      child: Row(
        children: [
          for (var index = 0; index < labels.length; index++) ...[
            Expanded(
              child: Column(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 180),
                    height: 5,
                    decoration: BoxDecoration(
                      color:
                          index <= current
                              ? const Color(0xFF2E7D32)
                              : Theme.of(context).dividerColor,
                      borderRadius: BorderRadius.circular(99),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    labels[index],
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight:
                          index == current ? FontWeight.w900 : FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            if (index < labels.length - 1) const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _MapStatusChip extends StatelessWidget {
  const _MapStatusChip({
    required this.icon,
    required this.label,
    required this.error,
  });

  final IconData icon;
  final String label;
  final bool error;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color:
          error
              ? Theme.of(context).colorScheme.errorContainer
              : Theme.of(context).colorScheme.surface.withValues(alpha: 0.94),
      borderRadius: BorderRadius.circular(16),
      boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
    ),
    child: Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w900),
            ),
          ),
        ],
      ),
    ),
  );
}

class _LocationFailure implements Exception {
  const _LocationFailure(this.message);
  final String message;
}
