import 'package:dio/dio.dart';

import '../config/admin_config.dart';

class AdminApiClient {
  AdminApiClient({
    String baseUrl = AdminConfig.apiBaseUrl,
    Dio? dio,
  }) : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: baseUrl,
                connectTimeout: AdminConfig.requestTimeout,
                receiveTimeout: AdminConfig.requestTimeout,
                headers: {
                  'Accept': 'application/json',
                },
              ),
            );

  final Dio _dio;

  Dio get dio => _dio;

  void setToken(String? token) {
    if (token == null || token.isEmpty) {
      _dio.options.headers.remove('Authorization');
      return;
    }

    _dio.options.headers['Authorization'] = 'Bearer $token';
  }
}
