import '../../barzegar/data/barzegar_models.dart';
import '../../farms/data/farm_models.dart';
import '../../notifications/data/notification_models.dart';
import '../../weather/data/weather_models.dart';

class HomeWeatherData {
  const HomeWeatherData({
    this.location,
    this.current,
    this.forecasts = const [],
    this.alerts = const [],
    this.farmPlot,
    this.farmWeather,
  });

  final WeatherLocationModel? location;
  final WeatherSnapshotModel? current;
  final List<WeatherForecastModel> forecasts;
  final List<WeatherAlertModel> alerts;
  final FarmPlotModel? farmPlot;
  final FarmWeatherModel? farmWeather;
}

class HomeDashboardData {
  const HomeDashboardData({
    this.farms = const [],
    this.weather = const HomeWeatherData(),
    this.conversations = const [],
    this.notifications = const [],
    this.unreadNotifications = 0,
    this.failedSections = const {},
  });

  final List<FarmModel> farms;
  final HomeWeatherData weather;
  final List<BarzegarConversation> conversations;
  final List<NotificationModel> notifications;
  final int unreadNotifications;
  final Set<String> failedSections;

  bool get hasPartialFailure => failedSections.isNotEmpty;
  BarzegarConversation? get latestConversation =>
      conversations.isEmpty ? null : conversations.first;
}
