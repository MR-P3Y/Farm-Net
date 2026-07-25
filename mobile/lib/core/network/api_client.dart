import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../storage/token_storage.dart';

class ApiClient {
  ApiClient({String? baseUrl, Dio? dio, TokenStorage? tokenStorage})
    : _tokenStorage = tokenStorage ?? TokenStorage(),
      _dio =
          dio ??
          Dio(
            BaseOptions(
              // اطمینان از وجود اسلش در پایان baseUrl برای جلوگیری از اختلال در مسیرها
              baseUrl:
                  (baseUrl ?? AppConfig.apiBaseUrl).endsWith('/')
                      ? (baseUrl ?? AppConfig.apiBaseUrl)
                      : '${baseUrl ?? AppConfig.apiBaseUrl}/',
              connectTimeout: AppConfig.requestTimeout,
              receiveTimeout: AppConfig.requestTimeout,
              sendTimeout: AppConfig.requestTimeout,
              headers: {'Accept': 'application/json'},
            ),
          ) {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _tokenStorage.getAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
  }

  final Dio _dio;
  final TokenStorage _tokenStorage;

  Dio get dio => _dio;

  void setToken(String? token) {
    if (token == null || token.isEmpty) {
      _dio.options.headers.remove('Authorization');
      return;
    }

    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return _dio.get(cleanPath, queryParameters: queryParameters);
  }

  Future<Response<dynamic>> post(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return _dio.post(cleanPath, data: data, queryParameters: queryParameters);
  }

  Future<Response<dynamic>> put(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return _dio.put(cleanPath, data: data, queryParameters: queryParameters);
  }

  Future<Response<dynamic>> patch(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return _dio.patch(cleanPath, data: data, queryParameters: queryParameters);
  }

  Future<Response<dynamic>> delete(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
  }) {
    final cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return _dio.delete(cleanPath, data: data, queryParameters: queryParameters);
  }
}
