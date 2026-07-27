class AdminAIOverview {
  const AdminAIOverview({
    required this.totalRequests,
    required this.queuedRequests,
    required this.runningRequests,
    required this.succeededRequests,
    required this.failedRequests,
    required this.blockedRequests,
    required this.totalInputTokens,
    required this.totalOutputTokens,
    required this.totalProviderCostToman,
    required this.pendingKnowledgeSources,
    required this.negativeFeedback,
    required this.reconciliationIssues,
  });
  final int totalRequests;
  final int queuedRequests;
  final int runningRequests;
  final int succeededRequests;
  final int failedRequests;
  final int blockedRequests;
  final int totalInputTokens;
  final int totalOutputTokens;
  final double totalProviderCostToman;
  final int pendingKnowledgeSources;
  final int negativeFeedback;
  final int reconciliationIssues;

  factory AdminAIOverview.fromJson(Map<String, dynamic> json) => AdminAIOverview(
    totalRequests: _int(json['total_requests']),
    queuedRequests: _int(json['queued_requests']),
    runningRequests: _int(json['running_requests']),
    succeededRequests: _int(json['succeeded_requests']),
    failedRequests: _int(json['failed_requests']),
    blockedRequests: _int(json['blocked_requests']),
    totalInputTokens: _int(json['total_input_tokens']),
    totalOutputTokens: _int(json['total_output_tokens']),
    totalProviderCostToman: _double(json['total_provider_cost_toman']),
    pendingKnowledgeSources: _int(json['pending_knowledge_sources']),
    negativeFeedback: _int(json['negative_feedback']),
    reconciliationIssues: _int(json['reconciliation_issues']),
  );
}

class AdminAIRequest {
  const AdminAIRequest({
    required this.id,
    required this.userId,
    required this.featureCode,
    required this.requestKind,
    required this.status,
    required this.priority,
    required this.attemptCount,
    required this.requestedAt,
    this.failureCode,
    this.safetyCode,
  });
  final int id;
  final int userId;
  final String featureCode;
  final String requestKind;
  final String status;
  final String priority;
  final int attemptCount;
  final String? failureCode;
  final String? safetyCode;
  final DateTime requestedAt;

  factory AdminAIRequest.fromJson(Map<String, dynamic> json) => AdminAIRequest(
    id: _int(json['id']),
    userId: _int(json['user_id']),
    featureCode: json['feature_code']?.toString() ?? '',
    requestKind: json['request_kind']?.toString() ?? '',
    status: json['status']?.toString() ?? '',
    priority: json['processing_priority']?.toString() ?? '',
    attemptCount: _int(json['attempt_count']),
    failureCode: json['failure_code']?.toString(),
    safetyCode: json['safety_code']?.toString(),
    requestedAt: DateTime.parse(json['requested_at'].toString()),
  );
}

class AdminAIKnowledgeSource {
  const AdminAIKnowledgeSource({
    required this.id,
    required this.code,
    required this.title,
    required this.publisher,
    required this.licenseCode,
    required this.licenseEvidence,
    required this.status,
    this.sourceUrl,
    this.reviewReason,
  });
  final int id;
  final String code;
  final String title;
  final String publisher;
  final String? sourceUrl;
  final String licenseCode;
  final String licenseEvidence;
  final String status;
  final String? reviewReason;

  factory AdminAIKnowledgeSource.fromJson(Map<String, dynamic> json) =>
      AdminAIKnowledgeSource(
        id: _int(json['id']),
        code: json['code']?.toString() ?? '',
        title: json['title']?.toString() ?? '',
        publisher: json['publisher']?.toString() ?? '',
        sourceUrl: json['source_url']?.toString(),
        licenseCode: json['license_code']?.toString() ?? '',
        licenseEvidence: json['license_evidence']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
        reviewReason: json['review_reason']?.toString(),
      );
}

class AdminAIUsage {
  const AdminAIUsage({
    required this.id,
    required this.requestId,
    required this.provider,
    required this.model,
    required this.inputTokens,
    required this.outputTokens,
    required this.latencyMs,
    this.costToman,
  });
  final int id;
  final int requestId;
  final String provider;
  final String model;
  final int inputTokens;
  final int outputTokens;
  final int latencyMs;
  final double? costToman;

  factory AdminAIUsage.fromJson(Map<String, dynamic> json) => AdminAIUsage(
    id: _int(json['id']),
    requestId: _int(json['request_id']),
    provider: json['provider_key']?.toString() ?? '',
    model: json['model_key']?.toString() ?? '',
    inputTokens: _int(json['input_tokens']),
    outputTokens: _int(json['output_tokens']),
    latencyMs: _int(json['latency_ms']),
    costToman:
        json['provider_cost_amount'] == null
            ? null
            : _double(json['provider_cost_amount']),
  );
}

class AdminAIPolicy {
  const AdminAIPolicy({
    required this.id,
    required this.key,
    required this.version,
    required this.requestKind,
    required this.status,
  });
  final int id;
  final String key;
  final String version;
  final String requestKind;
  final String status;

  factory AdminAIPolicy.fromJson(Map<String, dynamic> json) => AdminAIPolicy(
    id: _int(json['id']),
    key: json['policy_key']?.toString() ?? '',
    version: json['version']?.toString() ?? '',
    requestKind: json['request_kind']?.toString() ?? '',
    status: json['status']?.toString() ?? '',
  );
}

int _int(Object? value) => int.tryParse(value?.toString() ?? '') ?? 0;
double _double(Object? value) => double.tryParse(value?.toString() ?? '') ?? 0;
