import 'package:farm_net/features/notifications/data/notification_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('notification preference parses global channel override', () {
    final model = NotificationPreferenceModel.fromJson({
      'id': 4,
      'event_type': '*',
      'channel': 'push',
      'is_enabled': true,
    });
    expect(model.eventType, '*');
    expect(model.channel, 'push');
    expect(model.isEnabled, isTrue);
  });

  test('notification device output contains no token contract', () {
    final model = NotificationDeviceModel.fromJson({
      'id': 7,
      'platform': 'android',
      'is_active': true,
    });
    expect(model.id, 7);
    expect(model.platform, 'android');
    expect(model.isActive, isTrue);
  });
}
