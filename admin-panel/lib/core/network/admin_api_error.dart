class AdminApiError {
  const AdminApiError({
    required this.code,
    required this.message,
    this.details = const {},
    this.traceId,
  });

  final String code;
  final String message;
  final Map<String, dynamic> details;
  final String? traceId;

  factory AdminApiError.fromJson(Map<String, dynamic> json) {
    final error = json['error'] as Map<String, dynamic>? ?? {};
    final meta = json['meta'] as Map<String, dynamic>? ?? {};

    return AdminApiError(
      code: error['code']?.toString() ?? 'UNKNOWN_ERROR',
      message: error['message']?.toString() ?? 'Unknown error',
      details: (error['details'] as Map?)?.cast<String, dynamic>() ?? {},
      traceId: meta['trace_id']?.toString(),
    );
  }
}
