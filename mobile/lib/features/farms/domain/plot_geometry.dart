import 'dart:math' as math;

import 'package:latlong2/latlong.dart';

class PlotGeometry {
  const PlotGeometry._();

  static const _earthRadiusMetres = 6378137.0;

  static double areaSquareMetres(List<LatLng> vertices) {
    if (vertices.length < 3) return 0;

    final meanLatitude =
        vertices.fold<double>(0, (sum, point) => sum + point.latitude) /
        vertices.length;
    final cosLatitude = math.cos(_radians(meanLatitude));
    final projected = vertices
        .map(
          (point) => (
            x: _earthRadiusMetres * _radians(point.longitude) * cosLatitude,
            y: _earthRadiusMetres * _radians(point.latitude),
          ),
        )
        .toList(growable: false);

    var twiceArea = 0.0;
    for (var index = 0; index < projected.length; index++) {
      final current = projected[index];
      final next = projected[(index + 1) % projected.length];
      twiceArea += current.x * next.y - next.x * current.y;
    }
    return twiceArea.abs() / 2;
  }

  static LatLng center(List<LatLng> vertices, {required LatLng fallback}) {
    if (vertices.isEmpty) return fallback;
    final latitude =
        vertices.fold<double>(0, (sum, point) => sum + point.latitude) /
        vertices.length;
    final longitude =
        vertices.fold<double>(0, (sum, point) => sum + point.longitude) /
        vertices.length;
    return LatLng(latitude, longitude);
  }

  static List<Map<String, double>> closedBoundaryPayload(
    List<LatLng> vertices,
  ) {
    if (vertices.length < 3) return const [];
    final points = [vertices.first, ...vertices.skip(1), vertices.first];
    return points
        .map(
          (point) => {
            'latitude': _precision(point.latitude),
            'longitude': _precision(point.longitude),
          },
        )
        .toList(growable: false);
  }

  static bool hasSelfIntersection(List<LatLng> vertices) {
    if (vertices.length < 4) return false;
    final edgeCount = vertices.length;
    for (var first = 0; first < edgeCount; first++) {
      final firstNext = (first + 1) % edgeCount;
      for (var second = first + 1; second < edgeCount; second++) {
        final secondNext = (second + 1) % edgeCount;
        final adjacent =
            first == second ||
            firstNext == second ||
            secondNext == first ||
            (first == 0 && secondNext == 0);
        if (adjacent) continue;
        if (_segmentsIntersect(
          vertices[first],
          vertices[firstNext],
          vertices[second],
          vertices[secondNext],
        )) {
          return true;
        }
      }
    }
    return false;
  }

  static double _radians(double degrees) => degrees * math.pi / 180;

  static double _precision(double value) =>
      double.parse(value.toStringAsFixed(7));

  static bool _segmentsIntersect(LatLng a, LatLng b, LatLng c, LatLng d) {
    final o1 = _orientation(a, b, c);
    final o2 = _orientation(a, b, d);
    final o3 = _orientation(c, d, a);
    final o4 = _orientation(c, d, b);
    return o1 * o2 < 0 && o3 * o4 < 0;
  }

  static double _orientation(LatLng a, LatLng b, LatLng c) =>
      (b.longitude - a.longitude) * (c.latitude - a.latitude) -
      (b.latitude - a.latitude) * (c.longitude - a.longitude);
}
