import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../barzegar/data/barzegar_models.dart';
import '../../barzegar/data/barzegar_repository.dart';
import '../../farms/data/farm_models.dart';
import '../../farms/data/farm_repository.dart';
import '../../notifications/data/notification_models.dart';
import '../../notifications/data/notification_repository.dart';
import '../../weather/data/weather_models.dart';
import '../../weather/data/weather_repository.dart';
import 'home_dashboard_models.dart';

final homeDashboardRepositoryProvider = Provider<HomeDashboardRepository>(
  (ref) => HomeDashboardRepository(
    farms: ref.watch(farmRepositoryProvider),
    barzegar: ref.watch(barzegarRepositoryProvider),
    notifications: ref.watch(notificationRepositoryProvider),
    weather: ref.watch(weatherRepositoryProvider),
  ),
);

class HomeDashboardRepository {
  const HomeDashboardRepository({
    required FarmRepository farms,
    required BarzegarRepository barzegar,
    required NotificationRepository notifications,
    required WeatherRepository weather,
  }) : _farms = farms,
       _barzegar = barzegar,
       _notifications = notifications,
       _weather = weather;

  final FarmRepository _farms;
  final BarzegarRepository _barzegar;
  final NotificationRepository _notifications;
  final WeatherRepository _weather;

  Future<HomeDashboardData> load() async {
    var farms = <FarmModel>[];
    var conversations = <BarzegarConversation>[];
    var notifications = <NotificationModel>[];
    var unreadNotifications = 0;
    var weatherLocations = <WeatherLocationModel>[];
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
      () async {
        try {
          weatherLocations = _deduplicateLocations(
            await _weather.listLocations(),
          );
        } catch (_) {
          failed.add('weather');
        }
      }(),
    ]);

    final weatherSources = <HomeWeatherSource>[];
    for (final location in weatherLocations) {
      try {
        weatherSources.add(
          HomeWeatherSource.location(
            location: location,
            current: await _weather.current(location.id),
            alerts: await _weather.alerts(location.id),
          ),
        );
      } catch (_) {
        failed.add('weather');
      }
    }
    for (final farm in farms) {
      try {
        final plots = await _farms.plots(farm.id);
        for (final plot in plots.where(
          (item) => item.latitude != null && item.longitude != null,
        )) {
          try {
            weatherSources.add(
              HomeWeatherSource.farm(
                farm: farm,
                plot: plot,
                weather: await _farms.weather(farm.id, plot.id),
              ),
            );
          } catch (_) {
            failed.add('weather');
          }
        }
      } catch (_) {
        failed.add('weather');
      }
    }
    final weatherData = HomeWeatherData(sources: weatherSources);

    return HomeDashboardData(
      farms: farms,
      weather: weatherData,
      conversations: conversations,
      notifications: notifications,
      unreadNotifications: unreadNotifications,
      failedSections: failed,
    );
  }

  static List<WeatherLocationModel> _deduplicateLocations(
    List<WeatherLocationModel> values,
  ) {
    final result = <WeatherLocationModel>[];
    final ids = <int>{};
    WeatherLocationModel? gps;
    for (final value in values) {
      if (!ids.add(value.id)) continue;
      if (value.locationType == 'gps') {
        gps ??= value;
      } else {
        result.add(value);
      }
    }
    if (gps != null) result.insert(0, gps);
    return result;
  }
}
