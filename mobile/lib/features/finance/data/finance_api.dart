import 'package:dio/dio.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_error.dart';
import '../../../core/storage/token_storage.dart';
import 'finance_models.dart';

class FinanceApiException implements Exception {
  const FinanceApiException(this.error);
  final ApiError error;
  @override
  String toString() => error.message;
}

class FinanceApi {
  FinanceApi({ApiClient? client, TokenStorage? storage})
    : _client = client ?? ApiClient(baseUrl: AppConfig.apiBaseUrl),
      _storage = storage ?? TokenStorage();

  final ApiClient _client;
  final TokenStorage _storage;

  Future<WalletBalance> wallet() async {
    await _auth();
    try {
      final response = await _client.get('finance/wallet/me');
      return WalletBalance.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw FinanceApiException(_error(e));
    }
  }

  Future<List<Settlement>> settlements() async {
    await _auth();
    try {
      final response = await _client.get('finance/settlements/me');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => Settlement.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw FinanceApiException(_error(e));
    }
  }

  Future<Settlement> createSettlement(double amount, String? note) async {
    await _auth();
    final key = 'mobile-settlement-${DateTime.now().microsecondsSinceEpoch}';
    try {
      final response = await _client.post(
        'finance/settlements',
        data: {
          'amount': amount,
          'note': note,
          'currency': 'TOMAN',
          'idempotency_key': key,
        },
      );
      return Settlement.fromJson(
        response.data?['data'] as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw FinanceApiException(_error(e));
    }
  }

  Future<List<FinanceInvoice>> invoices() async {
    await _auth();
    try {
      final response = await _client.get('finance/invoices/me');
      final rows = response.data?['data'] as List? ?? [];
      return rows
          .map((item) => FinanceInvoice.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw FinanceApiException(_error(e));
    }
  }

  Future<void> _auth() async {
    _client.setToken(await _storage.getAccessToken());
  }

  ApiError _error(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) return ApiError.fromJson(data);
    return ApiError(
      code: 'NETWORK_ERROR',
      message: error.message ?? 'خطا در عملیات مالی',
    );
  }
}
