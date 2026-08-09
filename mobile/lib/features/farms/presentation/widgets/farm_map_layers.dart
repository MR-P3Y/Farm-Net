import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';

import '../../../../core/config/app_config.dart';
import '../../../../core/localization/app_localizations.dart';

enum FarmMapStyle { street, satellite }

extension FarmMapStyleConfig on FarmMapStyle {
  String get tileUrlTemplate =>
      this == FarmMapStyle.satellite
          ? AppConfig.mapSatelliteTileUrl
          : AppConfig.mapTileUrl;

  String get attribution =>
      this == FarmMapStyle.satellite
          ? AppConfig.mapSatelliteAttribution
          : '© OpenStreetMap contributors';
}

class FarmMapTiles extends StatelessWidget {
  const FarmMapTiles({required this.style, super.key});

  final FarmMapStyle style;

  @override
  Widget build(BuildContext context) => TileLayer(
    key: ValueKey(style),
    urlTemplate: style.tileUrlTemplate,
    userAgentPackageName: AppConfig.mapUserAgent,
    maxZoom: 19,
    errorTileCallback: (_, __, ___) {},
  );
}

class FarmMapAttribution extends StatelessWidget {
  const FarmMapAttribution({
    required this.style,
    this.bottomPadding = 6,
    super.key,
  });

  final FarmMapStyle style;
  final double bottomPadding;

  @override
  Widget build(BuildContext context) => IgnorePointer(
    key: ValueKey('farm-map-attribution-${style.name}'),
    child: SafeArea(
      child: Align(
        alignment: Alignment.bottomLeft,
        child: Padding(
          padding: EdgeInsets.fromLTRB(6, 0, 6, bottomPadding),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.62),
              borderRadius: BorderRadius.circular(6),
            ),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 360),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                child: Text(
                  style.attribution,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(color: Colors.white, fontSize: 9),
                ),
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

class FarmMapLayerToggle extends StatelessWidget {
  const FarmMapLayerToggle({
    required this.value,
    required this.onChanged,
    super.key,
  });

  final FarmMapStyle value;
  final ValueChanged<FarmMapStyle> onChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return SegmentedButton<FarmMapStyle>(
      key: const ValueKey('farm-map-layer-toggle'),
      showSelectedIcon: false,
      segments: [
        ButtonSegment(
          value: FarmMapStyle.street,
          icon: const Icon(
            Icons.map_outlined,
            key: ValueKey('farm-map-style-street'),
          ),
          label: Text(l10n.tr(fa: 'خیابانی', en: 'Street')),
        ),
        ButtonSegment(
          value: FarmMapStyle.satellite,
          icon: const Icon(
            Icons.satellite_alt_outlined,
            key: ValueKey('farm-map-style-satellite'),
          ),
          label: Text(l10n.tr(fa: 'ماهواره‌ای', en: 'Satellite')),
        ),
      ],
      selected: {value},
      onSelectionChanged: (selection) => onChanged(selection.first),
    );
  }
}
