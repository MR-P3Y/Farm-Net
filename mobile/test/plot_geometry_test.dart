import 'package:farm_net/features/farms/domain/plot_geometry.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';

void main() {
  test('map vertices calculate a stable agricultural plot area', () {
    const vertices = [
      LatLng(35.0000, 51.0000),
      LatLng(35.0000, 51.0011),
      LatLng(35.0009, 51.0011),
      LatLng(35.0009, 51.0000),
    ];

    final area = PlotGeometry.areaSquareMetres(vertices);

    expect(area, greaterThan(9800));
    expect(area, lessThan(10250));
  });

  test('boundary payload is closed and rounded for the backend contract', () {
    const vertices = [
      LatLng(35.123456789, 51.123456789),
      LatLng(35.123456789, 51.124456789),
      LatLng(35.124456789, 51.124456789),
    ];

    final payload = PlotGeometry.closedBoundaryPayload(vertices);

    expect(payload, hasLength(4));
    expect(payload.first, payload.last);
    expect(payload.first['latitude'], 35.1234568);
    expect(payload.first['longitude'], 51.1234568);
  });

  test('crossed plot boundaries are rejected before submission', () {
    const crossed = [
      LatLng(35.0, 51.0),
      LatLng(35.001, 51.001),
      LatLng(35.0, 51.001),
      LatLng(35.001, 51.0),
    ];
    const rectangle = [
      LatLng(35.0, 51.0),
      LatLng(35.0, 51.001),
      LatLng(35.001, 51.001),
      LatLng(35.001, 51.0),
    ];

    expect(PlotGeometry.hasSelfIntersection(crossed), isTrue);
    expect(PlotGeometry.hasSelfIntersection(rectangle), isFalse);
  });
}
