import 'package:farm_net/features/farms/domain/farm_profile_input.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('farm area accepts Persian and Arabic digits', () {
    expect(parseFarmArea('۱۲۵۰۰٫۵'), 12500.5);
    expect(parseFarmArea('١٢٥٠٠'), 12500);
  });

  test('farm area accepts grouping separators and optional empty input', () {
    expect(parseFarmArea('12,500'), 12500);
    expect(parseFarmArea('۱۲٬۵۰۰'), 12500);
    expect(parseFarmArea('  '), isNull);
    expect(parseFarmArea('not-a-number'), isNull);
  });

  test('existing whole area is formatted without a decimal suffix', () {
    expect(formatFarmAreaInput(12500), '12500');
    expect(formatFarmAreaInput(12500.5), '12500.5');
    expect(formatFarmAreaInput(null), '');
  });
}
