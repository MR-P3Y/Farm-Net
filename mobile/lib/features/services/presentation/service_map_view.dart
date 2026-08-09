import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/localization/app_localizations.dart';
import '../../farms/presentation/widgets/farm_map_layers.dart';
import '../data/service_models.dart';

class ServiceMapView extends StatefulWidget {
  const ServiceMapView({
    required this.offers,
    this.userLatitude,
    this.userLongitude,
    super.key,
  });

  final List<ServiceOffer> offers;
  final double? userLatitude;
  final double? userLongitude;

  @override
  State<ServiceMapView> createState() => _ServiceMapViewState();
}

class _ServiceMapViewState extends State<ServiceMapView> {
  FarmMapStyle _style = FarmMapStyle.street;

  @override
  Widget build(BuildContext context) {
    final located = widget.offers
        .where((item) => item.latitude != null && item.longitude != null)
        .toList(growable: false);
    if (located.isEmpty) {
      return SizedBox(
        height: 360,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(28),
            child: Text(
              context.l10n.tr(
                fa: 'برای خدمات پیدا‌شده هنوز موقعیت نقشه ثبت نشده است.',
                en: 'The matching services do not have map locations yet.',
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    final initial =
        widget.userLatitude != null && widget.userLongitude != null
            ? LatLng(widget.userLatitude!, widget.userLongitude!)
            : LatLng(located.first.latitude!, located.first.longitude!);
    final colors = Theme.of(context).colorScheme;

    return SizedBox(
      height: 520,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: Stack(
          children: [
            FlutterMap(
              options: MapOptions(initialCenter: initial, initialZoom: 11),
              children: [
                FarmMapTiles(style: _style),
                MarkerLayer(
                  markers: [
                    if (widget.userLatitude != null &&
                        widget.userLongitude != null)
                      Marker(
                        point: LatLng(
                          widget.userLatitude!,
                          widget.userLongitude!,
                        ),
                        width: 52,
                        height: 52,
                        child: Tooltip(
                          message: context.l10n.tr(
                            fa: 'موقعیت من',
                            en: 'My location',
                          ),
                          child: Icon(
                            Icons.my_location_rounded,
                            color: colors.tertiary,
                            size: 34,
                            shadows: const [
                              Shadow(color: Colors.white, blurRadius: 5),
                            ],
                          ),
                        ),
                      ),
                    for (final offer in located)
                      Marker(
                        point: LatLng(offer.latitude!, offer.longitude!),
                        width: 58,
                        height: 58,
                        alignment: Alignment.topCenter,
                        child: Tooltip(
                          message: offer.title,
                          child: GestureDetector(
                            key: ValueKey('service-map-offer-${offer.id}'),
                            onTap: () => context.push('/services/${offer.id}'),
                            child: Icon(
                              Icons.location_on_rounded,
                              size: 48,
                              color: colors.primary,
                              shadows: const [
                                Shadow(color: Colors.white, blurRadius: 5),
                              ],
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                FarmMapAttribution(style: _style),
              ],
            ),
            PositionedDirectional(
              top: 12,
              start: 12,
              child: Material(
                elevation: 3,
                color: colors.surface.withValues(alpha: .92),
                borderRadius: BorderRadius.circular(16),
                clipBehavior: Clip.antiAlias,
                child: Padding(
                  padding: const EdgeInsets.all(4),
                  child: FarmMapLayerToggle(
                    value: _style,
                    onChanged: (value) => setState(() => _style = value),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
