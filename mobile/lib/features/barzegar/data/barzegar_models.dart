class BarzegarConversation {
  const BarzegarConversation({
    required this.id,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.title,
    this.messages = const [],
  });

  final int id;
  final String? title;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<BarzegarMessage> messages;

  factory BarzegarConversation.fromJson(Map<String, dynamic> json) =>
      BarzegarConversation(
        id: (json['id'] as num).toInt(),
        title: json['title']?.toString(),
        status: json['status']?.toString() ?? 'active',
        createdAt: DateTime.parse(json['created_at'].toString()),
        updatedAt: DateTime.parse(json['updated_at'].toString()),
        messages:
            (json['messages'] as List? ?? const [])
                .whereType<Map>()
                .map(
                  (item) => BarzegarMessage.fromJson(
                    item.cast<String, dynamic>(),
                  ),
                )
                .toList(),
      );
}

class BarzegarMessage {
  const BarzegarMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.createdAt,
    this.requestId,
    this.safetyLabel,
  });

  final int id;
  final int? requestId;
  final String role;
  final String content;
  final String? safetyLabel;
  final DateTime createdAt;

  bool get isUser => role == 'user';

  factory BarzegarMessage.fromJson(Map<String, dynamic> json) =>
      BarzegarMessage(
        id: (json['id'] as num).toInt(),
        requestId: (json['request_id'] as num?)?.toInt(),
        role: json['role']?.toString() ?? '',
        content: json['content']?.toString() ?? '',
        safetyLabel: json['safety_label']?.toString(),
        createdAt: DateTime.parse(json['created_at'].toString()),
      );
}

class BarzegarRequest {
  const BarzegarRequest({
    required this.id,
    required this.conversationId,
    required this.featureCode,
    required this.requestKind,
    required this.status,
    required this.requestedAt,
    this.failureCode,
    this.safetyCode,
    this.consultRequestId,
  });

  final int id;
  final int conversationId;
  final String featureCode;
  final String requestKind;
  final String status;
  final String? failureCode;
  final String? safetyCode;
  final int? consultRequestId;
  final DateTime requestedAt;

  bool get isPending => status == 'queued' || status == 'running';

  factory BarzegarRequest.fromJson(Map<String, dynamic> json) =>
      BarzegarRequest(
        id: (json['id'] as num).toInt(),
        conversationId: (json['conversation_id'] as num).toInt(),
        featureCode: json['feature_code']?.toString() ?? '',
        requestKind: json['request_kind']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
        failureCode: json['failure_code']?.toString(),
        safetyCode: json['safety_code']?.toString(),
        consultRequestId: (json['consult_request_id'] as num?)?.toInt(),
        requestedAt: DateTime.parse(json['requested_at'].toString()),
      );
}

class BarzegarContextConsent {
  const BarzegarContextConsent({
    required this.id,
    required this.farmId,
    required this.purpose,
    required this.status,
    this.plotId,
    this.cropCycleId,
  });

  final int id;
  final int farmId;
  final int? plotId;
  final int? cropCycleId;
  final String purpose;
  final String status;

  factory BarzegarContextConsent.fromJson(Map<String, dynamic> json) =>
      BarzegarContextConsent(
        id: (json['id'] as num).toInt(),
        farmId: (json['farm_id'] as num).toInt(),
        plotId: (json['plot_id'] as num?)?.toInt(),
        cropCycleId: (json['crop_cycle_id'] as num?)?.toInt(),
        purpose: json['purpose']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
      );
}

class BarzegarDiarySuggestion {
  const BarzegarDiarySuggestion({
    required this.id,
    required this.requestId,
    required this.farmId,
    required this.plotId,
    required this.cropCycleId,
    required this.proposedOperation,
    required this.status,
    required this.createdAt,
    this.farmOperationId,
    this.rejectionReason,
  });

  final int id;
  final int requestId;
  final int farmId;
  final int plotId;
  final int cropCycleId;
  final Map<String, dynamic> proposedOperation;
  final String status;
  final int? farmOperationId;
  final String? rejectionReason;
  final DateTime createdAt;

  factory BarzegarDiarySuggestion.fromJson(Map<String, dynamic> json) =>
      BarzegarDiarySuggestion(
        id: (json['id'] as num).toInt(),
        requestId: (json['request_id'] as num).toInt(),
        farmId: (json['farm_id'] as num).toInt(),
        plotId: (json['plot_id'] as num).toInt(),
        cropCycleId: (json['crop_cycle_id'] as num).toInt(),
        proposedOperation:
            (json['proposed_operation'] as Map).cast<String, dynamic>(),
        status: json['status']?.toString() ?? '',
        farmOperationId: (json['farm_operation_id'] as num?)?.toInt(),
        rejectionReason: json['rejection_reason']?.toString(),
        createdAt: DateTime.parse(json['created_at'].toString()),
      );
}

class BarzegarFarmerReport {
  const BarzegarFarmerReport({
    required this.id,
    required this.requestId,
    required this.farmId,
    required this.sourceSnapshot,
    required this.narrative,
    required this.generatedAt,
    this.plotId,
    this.cropCycleId,
  });

  final int id;
  final int requestId;
  final int farmId;
  final int? plotId;
  final int? cropCycleId;
  final Map<String, dynamic> sourceSnapshot;
  final String narrative;
  final DateTime generatedAt;

  factory BarzegarFarmerReport.fromJson(Map<String, dynamic> json) =>
      BarzegarFarmerReport(
        id: (json['id'] as num).toInt(),
        requestId: (json['request_id'] as num).toInt(),
        farmId: (json['farm_id'] as num).toInt(),
        plotId: (json['plot_id'] as num?)?.toInt(),
        cropCycleId: (json['crop_cycle_id'] as num?)?.toInt(),
        sourceSnapshot:
            (json['source_snapshot'] as Map).cast<String, dynamic>(),
        narrative: json['narrative']?.toString() ?? '',
        generatedAt: DateTime.parse(json['generated_at'].toString()),
      );
}

class BarzegarFeature {
  const BarzegarFeature({
    required this.label,
    required this.featureCode,
    required this.requestKind,
    required this.contextPurpose,
    this.requiresCycle = false,
    this.requiresImage = false,
  });

  final String label;
  final String featureCode;
  final String requestKind;
  final String? contextPurpose;
  final bool requiresCycle;
  final bool requiresImage;
}

const barzegarFeatures = <BarzegarFeature>[
  BarzegarFeature(
    label: 'پرسش عمومی',
    featureCode: 'ai.text_chat',
    requestKind: 'text',
    contextPurpose: null,
  ),
  BarzegarFeature(
    label: 'تحلیل مزرعه',
    featureCode: 'ai.farm_context',
    requestKind: 'farm_context',
    contextPurpose: 'answer_question',
  ),
  BarzegarFeature(
    label: 'تحلیل عمیق',
    featureCode: 'ai.deep_analysis',
    requestKind: 'deep_analysis',
    contextPurpose: 'deep_analysis',
  ),
  BarzegarFeature(
    label: 'تحلیل تصویر',
    featureCode: 'ai.image_analysis',
    requestKind: 'image_analysis',
    contextPurpose: 'image_analysis',
    requiresImage: true,
  ),
  BarzegarFeature(
    label: 'پیشنهاد دفتر',
    featureCode: 'ai.smart_diary',
    requestKind: 'smart_diary',
    contextPurpose: 'smart_diary',
    requiresCycle: true,
  ),
  BarzegarFeature(
    label: 'گزارش کشاورز',
    featureCode: 'ai.report_export',
    requestKind: 'report',
    contextPurpose: 'report',
  ),
];
