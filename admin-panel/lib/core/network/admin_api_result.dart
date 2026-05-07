import 'admin_api_error.dart';

sealed class AdminApiResult<T> {
  const AdminApiResult();
}

class AdminApiSuccess<T> extends AdminApiResult<T> {
  const AdminApiSuccess(this.data);

  final T data;
}

class AdminApiFailure<T> extends AdminApiResult<T> {
  const AdminApiFailure(this.error);

  final AdminApiError error;
}
