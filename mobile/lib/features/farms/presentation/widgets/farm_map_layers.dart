import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';

import '../../../../core/config/app_config.dart';

class FarmMapTiles extends StatelessWidget {
  const FarmMapTiles({super.key});

  @override
  Widget build(BuildContext context) => TileLayer(
    urlTemplate: AppConfig.mapTileUrl,
    userAgentPackageName: AppConfig.mapUserAgent,
    maxZoom: 19,
    errorTileCallback: (_, __, ___) {},
  );
}

class FarmMapAttribution extends StatelessWidget {
  const FarmMapAttribution({super.key});

  @override
  Widget build(BuildContext context) => const RichAttributionWidget(
    popupInitialDisplayDuration: Duration(seconds: 3),
    showFlutterMapAttribution: false,
    attributions: [TextSourceAttribution('© OpenStreetMap contributors')],
  );
}
