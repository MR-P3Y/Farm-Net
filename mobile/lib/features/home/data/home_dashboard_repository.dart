import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../barzegar/data/barzegar_models.dart';
import '../../barzegar/data/barzegar_repository.dart';
import '../../farms/data/farm_models.dart';
import '../../farms/data/farm_repository.dart';
import '../../notifications/data/notification_models.dart';
import '../../notifications/data/notification_repository.dart';
import 'home_dashboard_models.dart';

final homeDashboardRepositoryProvider = Provider<HomeDashboardRepository>(
  (ref) => HomeDashboardRepository(
    farms: ref.watch(farmRepositoryProvider),
    barzegar: ref.watch(barzegarRepositoryProvider),
    notifications: ref.watch(notificationRepositoryProvider),
  ),
);

class HomeDashboardRepository {
  const HomeDashboardRepository({
    required FarmRepository farms,
    required BarzegarRepository barzegar,
    required NotificationRepository notifications,
  }) : _farms = farms,
       _barzegar = barzegar,
       _notifications = notifications;

  final FarmRepository _farms;
  final BarzegarRepository _barzegar;
  final NotificationRepository _notifications;

  Future<HomeDashboardData> load() async {
    var farms = <FarmModel>[];
    var conversations = <BarzegarConversation>[];
    var notifications = <NotificationModel>[];
    var unreadNotifications = 0;
    final failed = <String>{};

    await Future.wait<void>([
      () async {
        try {
          farms = await _farms.farms();
        } catch (_) {
          failed.add('farms');
        }
      }(),
      () async {
        try {
          conversations = await _barzegar.conversations();
          conversations.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
        } catch (_) {
          failed.add('barzegar');
        }
      }(),
      () async {
        try {
          notifications = await _notifications.listMyNotifications(pageSize: 5);
          unreadNotifications = await _notifications.unreadCount();
        } catch (_) {
          failed.add('notifications');
        }
      }(),
    ]);

    var weatherData = const HomeWeatherData();
    if (farms.isNotEmpty) {
      try {
        final plots = await _farms.plots(farms.first.id);
        final located = plots.where(
          (plot) => plot.latitude != null && plot.longitude != null,
        );
        final plot = located.isNotEmpty ? located.first : plots.firstOrNull;
        if (plot != null && plot.latitude != null && plot.longitude != null) {
          weatherData = HomeWeatherData(
            farmPlot: plot,
            farmWeather: await _farms.weather(farms.first.id, plot.id),
          );
        } else {
          weatherData = HomeWeatherData(farmPlot: plot);
        }
      } catch (_) {
        failed.add('weather');
      }
    }

    return HomeDashboardData(
      farms: farms,
      weather: weatherData,
      conversations: conversations,
      notifications: notifications,
      unreadNotifications: unreadNotifications,
      failedSections: failed,
    );
  }
}
