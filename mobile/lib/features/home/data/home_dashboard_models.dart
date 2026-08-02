import '../../barzegar/data/barzegar_models.dart';
import '../../farms/data/farm_models.dart';
import '../../notifications/data/notification_models.dart';
import '../../weather/data/weather_models.dart';

class HomeWeatherData {
  const HomeWeatherData({
    this.sources = const [],
    this.location,
    this.current,
    this.forecasts = const [],
    this.alerts = const [],
    this.farmPlot,
    this.farmWeather,
  });

  final List<HomeWeatherSource> sources;

  final WeatherLocationModel? location;
  final WeatherSnapshotModel? current;
  final List<WeatherForecastModel> forecasts;
  final List<WeatherAlertModel> alerts;
  final FarmPlotModel? farmPlot;
  final FarmWeatherModel? farmWeather;

  List<HomeWeatherSource> get effectiveSources {
    if (sources.isNotEmpty) return sources;
    if (farmPlot != null) {
      return [HomeWeatherSource.farm(plot: farmPlot!, weather: farmWeather)];
    }
    if (location != null) {
      return [
        HomeWeatherSource.location(
          location: location!,
          current: current,
          forecasts: forecasts,
          alerts: alerts,
        ),
      ];
    }
    return const [];
  }
}

class HomeWeatherSource {
  const HomeWeatherSource._({
    required this.key,
    this.location,
    this.current,
    this.forecasts = const [],
    this.alerts = const [],
    this.farm,
    this.farmPlot,
    this.farmWeather,
  });

  factory HomeWeatherSource.location({
    required WeatherLocationModel location,
    WeatherSnapshotModel? current,
    List<WeatherForecastModel> forecasts = const [],
    List<WeatherAlertModel> alerts = const [],
  }) => HomeWeatherSource._(
    key: 'location:${location.id}',
    location: location,
    current: current,
    forecasts: forecasts,
    alerts: alerts,
  );

  factory HomeWeatherSource.farm({
    FarmModel? farm,
    required FarmPlotModel plot,
    FarmWeatherModel? weather,
  }) => HomeWeatherSource._(
    key: 'farm:${farm?.id ?? plot.farmId}:plot:${plot.id}',
    farm: farm,
    farmPlot: plot,
    farmWeather: weather,
  );

  final String key;
  final WeatherLocationModel? location;
  final WeatherSnapshotModel? current;
  final List<WeatherForecastModel> forecasts;
  final List<WeatherAlertModel> alerts;
  final FarmModel? farm;
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
