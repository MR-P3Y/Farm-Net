import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/localization/app_localizations.dart';
import '../../data/farm_models.dart';
import '../../domain/plot_geometry.dart';
import 'farm_map_layers.dart';

class FarmPlotsMap extends StatefulWidget {
  const FarmPlotsMap({required this.plots, required this.onPlotTap, super.key});

  final List<FarmPlotModel> plots;
  final ValueChanged<FarmPlotModel> onPlotTap;

  @override
  State<FarmPlotsMap> createState() => _FarmPlotsMapState();
}

class _FarmPlotsMapState extends State<FarmPlotsMap> {
  var _mapStyle = FarmMapStyle.street;

  @override
  Widget build(BuildContext context) {
    final located = widget.plots.where((plot) => plot.hasLocation).toList();
    if (located.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Text(
            context.l10n.tr(
              fa: 'هنوز برای هیچ قطعه‌ای موقعیت نقشه ثبت نشده است.',
              en: 'No Plot has a saved map location yet.',
            ),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final centers = <int, LatLng>{};
    for (final plot in located) {
      final fallback = LatLng(plot.latitude!, plot.longitude!);
      final vertices = _vertices(plot);
      centers[plot.id] = PlotGeometry.center(vertices, fallback: fallback);
    }
    final initial = centers[located.first.id]!;

    return Stack(
      children: [
        Positioned.fill(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: FlutterMap(
              options: MapOptions(initialCenter: initial, initialZoom: 14),
              children: [
                FarmMapTiles(style: _mapStyle),
                PolygonLayer(
                  polygons: [
                    for (final plot in located)
                      if (_vertices(plot).length >= 3)
                        Polygon(
                          points: _vertices(plot),
                          color: const Color(
                            0xFF2E7D32,
                          ).withValues(alpha: 0.22),
                          borderColor: const Color(0xFF0F4D2E),
                          borderStrokeWidth: 3,
                          label: plot.name,
                          labelStyle: TextStyle(
                            color:
                                _mapStyle == FarmMapStyle.satellite
                                    ? Colors.white
                                    : const Color(0xFF0F4D2E),
                            fontWeight: FontWeight.w900,
                            shadows:
                                _mapStyle == FarmMapStyle.satellite
                                    ? const [
                                      Shadow(
                                        color: Colors.black87,
                                        blurRadius: 5,
                                      ),
                                    ]
                                    : null,
                          ),
                        ),
                  ],
                ),
                MarkerLayer(
                  markers: [
                    for (final plot in located)
                      Marker(
                        point: centers[plot.id]!,
                        width: 58,
                        height: 58,
                        alignment: Alignment.topCenter,
                        child: Tooltip(
                          message:
                              plot.locationLabel == null || !context.l10n.isFa
                                  ? plot.name
                                  : '${plot.name}\n${plot.locationLabel}',
                          child: GestureDetector(
                            key: ValueKey('farm-plot-map-${plot.id}'),
                            onTap: () => widget.onPlotTap(plot),
                            child: const Icon(
                              Icons.location_on_rounded,
                              size: 46,
                              color: Color(0xFF0F4D2E),
                              shadows: [
                                Shadow(color: Colors.white, blurRadius: 4),
                              ],
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                FarmMapAttribution(style: _mapStyle),
              ],
            ),
          ),
        ),
        PositionedDirectional(
          top: 12,
          start: 12,
          child: Material(
            elevation: 3,
            color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.9),
            borderRadius: BorderRadius.circular(16),
            clipBehavior: Clip.antiAlias,
            child: Padding(
              padding: const EdgeInsets.all(4),
              child: FarmMapLayerToggle(
                value: _mapStyle,
                onChanged: (value) => setState(() => _mapStyle = value),
              ),
            ),
          ),
        ),
      ],
    );
  }

  static List<LatLng> _vertices(FarmPlotModel plot) => plot.boundary
      .map((point) => LatLng(point.latitude, point.longitude))
      .toList(growable: false);
}
