import 'package:farm_net_admin/features/ai/data/admin_ai_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('overview parses TOMAN cost and safety counters', () {
    final value = AdminAIOverview.fromJson({
      'total_requests': 10,
      'queued_requests': 2,
      'running_requests': 1,
      'succeeded_requests': 5,
      'failed_requests': 1,
      'blocked_requests': 1,
      'total_input_tokens': 120,
      'total_output_tokens': 45,
      'total_provider_cost_toman': '1250.50',
      'pending_knowledge_sources': 2,
      'negative_feedback': 1,
      'reconciliation_issues': 0,
    });
    expect(value.totalProviderCostToman, 1250.5);
    expect(value.blockedRequests, 1);
  });

  test('request model contains metadata but no private content', () {
    final value = AdminAIRequest.fromJson({
      'id': 3,
      'user_id': 9,
      'feature_code': 'ai.image_analysis',
      'request_kind': 'image_analysis',
      'status': 'blocked',
      'processing_priority': 'standard',
      'attempt_count': 1,
      'failure_code': 'AI_OUTPUT_INVALID',
      'safety_code': 'IMAGE_EVIDENCE_GATED',
      'requested_at': '2026-07-28T12:00:00',
    });
    expect(value.safetyCode, 'IMAGE_EVIDENCE_GATED');
    expect(value.status, 'blocked');
  });

  test('knowledge source parses governed lifecycle', () {
    final value = AdminAIKnowledgeSource.fromJson({
      'id': 4,
      'code': 'ministry.guide',
      'title': 'راهنما',
      'publisher': 'وزارت',
      'source_url': null,
      'license_code': 'internal',
      'license_evidence': 'مجوز ثبت‌شده',
      'status': 'in_review',
      'review_reason': null,
    });
    expect(value.status, 'in_review');
    expect(value.licenseEvidence, isNotEmpty);
  });
}
