import 'package:farm_net_admin/features/notifications/data/admin_notification_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('delivery detail parses attempts and provider errors', () {
    final delivery = AdminDeliveryModel.fromJson({
      'id': 41,
      'notification_id': 12,
      'channel': 'email',
      'status': 'failed',
      'attempt_count': 2,
      'max_attempts': 5,
      'provider': 'smtp',
      'error_code': 'timeout',
      'error_message': 'Provider timeout',
      'next_attempt_at': '2026-07-18T08:00:00Z',
      'created_at': '2026-07-18T07:00:00Z',
      'attempts': [
        {
          'attempt_number': 2,
          'status': 'failed',
          'provider': 'smtp',
          'error_code': 'timeout',
          'error_message': 'Provider timeout',
          'started_at': '2026-07-18T07:10:00Z',
          'finished_at': '2026-07-18T07:10:05Z',
        },
      ],
    });

    expect(delivery.errorCode, 'timeout');
    expect(delivery.attempts, hasLength(1));
    expect(delivery.attempts.single.attemptNumber, 2);
    expect(delivery.attempts.single.finishedAt, isNotNull);
    expect(delivery.canRetry, isTrue);
  });

  test('retry eligibility follows delivery contract', () {
    AdminDeliveryModel model(String channel, String status) =>
        AdminDeliveryModel.fromJson({
          'id': 1,
          'notification_id': 2,
          'channel': channel,
          'status': status,
          'attempt_count': 1,
          'max_attempts': 5,
          'created_at': '2026-07-18T07:00:00Z',
        });

    expect(model('email', 'failed').canRetry, isTrue);
    expect(model('email', 'sent').canRetry, isFalse);
    expect(model('in_app', 'failed').canRetry, isFalse);
  });
}
