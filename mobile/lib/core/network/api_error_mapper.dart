import 'package:dio/dio.dart';

import 'api_error.dart';

ApiError mapApiError(Object error) {
  if (error is DioException) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      return ApiError.fromJson(data);
    }

    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network error',
    );
  }

  return ApiError(
    code: 'UNKNOWN_ERROR',
    message: error.toString(),
  );
}
