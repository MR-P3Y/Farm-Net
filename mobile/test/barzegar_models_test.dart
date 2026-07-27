import 'package:farm_net/features/barzegar/data/barzegar_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('request parses lifecycle and pending states', () {
    final request = BarzegarRequest.fromJson({
      'id': 9,
      'conversation_id': 3,
      'feature_code': 'ai.smart_diary',
      'request_kind': 'smart_diary',
      'status': 'queued',
      'failure_code': null,
      'safety_code': null,
      'consult_request_id': null,
      'requested_at': '2026-07-28T10:00:00',
    });

    expect(request.isPending, isTrue);
    expect(request.requestKind, 'smart_diary');
  });

  test('diary suggestion keeps typed proposal and operation link', () {
    final suggestion = BarzegarDiarySuggestion.fromJson({
      'id': 1,
      'request_id': 9,
      'farm_id': 2,
      'plot_id': 4,
      'crop_cycle_id': 7,
      'proposed_operation': {
        'operation_type': 'irrigation',
        'title': 'آبیاری',
        'occurred_on': '2026-07-28',
      },
      'status': 'accepted',
      'farm_operation_id': 21,
      'rejection_reason': null,
      'created_at': '2026-07-28T10:00:00',
    });

    expect(suggestion.proposedOperation['operation_type'], 'irrigation');
    expect(suggestion.farmOperationId, 21);
  });

  test('farmer report parses real source snapshot counts', () {
    final report = BarzegarFarmerReport.fromJson({
      'id': 5,
      'request_id': 10,
      'farm_id': 2,
      'plot_id': null,
      'crop_cycle_id': null,
      'source_snapshot': {
        'operation_count': 6,
        'input_count': 2,
        'harvest_count': 1,
      },
      'narrative': 'گزارش مزرعه',
      'generated_at': '2026-07-28T10:00:00',
    });

    expect(report.sourceSnapshot['operation_count'], 6);
    expect(report.narrative, 'گزارش مزرعه');
  });

  test('feature catalog covers all backend request kinds', () {
    expect(
      barzegarFeatures.map((item) => item.requestKind).toSet(),
      {
        'text',
        'farm_context',
        'deep_analysis',
        'image_analysis',
        'smart_diary',
        'report',
      },
    );
    expect(
      barzegarFeatures
          .singleWhere((item) => item.requestKind == 'smart_diary')
          .requiresCycle,
      isTrue,
    );
  });
}
