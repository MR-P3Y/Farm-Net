import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/network/api_error_mapper.dart';
import 'finance_models.dart';

class FinanceApiException implements Exception {
  const FinanceApiException(this.error);
  final ApiError error;
}

class FinanceApi {
  FinanceApi({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl);
  final ApiClient _client;

  Future<WalletBalance> wallet() async => _request(() async {
    final response = await _client.dio.get<Map<String, dynamic>>(
      '/finance/wallet/me',
    );
    return WalletBalance.fromJson(
      response.data!['data'] as Map<String, dynamic>,
    );
  });

  Future<List<FinanceInvoice>> invoices() async => _request(() async {
    final response = await _client.dio.get<Map<String, dynamic>>(
      '/finance/invoices/me',
    );
    return _list(response.data?['data'], FinanceInvoice.fromJson);
  });

  Future<List<Settlement>> settlements() async => _request(() async {
    final response = await _client.dio.get<Map<String, dynamic>>(
      '/finance/settlements/me',
    );
    return _list(response.data?['data'], Settlement.fromJson);
  });

  Future<Settlement> createSettlement(
    double amount,
    String? note,
  ) async => _request(() async {
    final key = 'mobile-settlement-${DateTime.now().microsecondsSinceEpoch}';
    final response = await _client.dio.post<Map<String, dynamic>>(
      '/finance/settlements',
      data: {
        'amount': amount,
        'currency': 'TOMAN',
        'idempotency_key': key,
        'note': note?.trim().isEmpty == true ? null : note?.trim(),
      },
    );
    return Settlement.fromJson(response.data!['data'] as Map<String, dynamic>);
  });

  Future<T> _request<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (error) {
      throw FinanceApiException(mapApiError(error));
    }
  }

  List<T> _list<T>(dynamic data, T Function(Map<String, dynamic>) parser) =>
      (data as List? ?? const [])
          .map((row) => parser(row as Map<String, dynamic>))
          .toList();
}
