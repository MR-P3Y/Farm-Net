import 'package:farm_net/features/consultants/state/consultant_list_state.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('consultant discovery defaults to rating and preserves filters', () {
    final state = ConsultantListState.initial().copyWith(
      selectedSpecialtyId: 4,
      query: 'گیاه',
      sort: 'newest',
    );

    expect(state.selectedSpecialtyId, 4);
    expect(state.query, 'گیاه');
    expect(state.sort, 'newest');
  });

  test('consultant discovery can clear the selected specialty', () {
    final selected = ConsultantListState.initial().copyWith(
      selectedSpecialtyId: 4,
    );
    final cleared = selected.copyWith(selectedSpecialtyId: null);

    expect(cleared.selectedSpecialtyId, isNull);
    expect(cleared.sort, 'rating');
  });
}
