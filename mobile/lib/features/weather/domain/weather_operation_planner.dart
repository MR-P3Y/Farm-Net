import '../data/weather_models.dart';

enum WeatherOperationType {
  spraying,
  irrigation,
  fertilizing,
  harvest,
  machinery,
}

class WeatherOperationPlan {
  const WeatherOperationPlan({
    required this.operation,
    required this.isSuitable,
    required this.score,
    required this.reasonCodes,
    this.startsAt,
    this.endsAt,
  });

  final WeatherOperationType operation;
  final bool isSuitable;
  final int score;
  final DateTime? startsAt;
  final DateTime? endsAt;
  final List<String> reasonCodes;
}

class WeatherOperationPlanner {
  const WeatherOperationPlanner();

  List<WeatherOperationPlan> plan(
    List<WeatherForecastModel> forecasts, {
    DateTime? now,
  }) {
    final current = (now ?? DateTime.now()).toLocal();
    final horizon = current.add(const Duration(hours: 48));
    final slots =
        forecasts
            .map(_Slot.fromForecast)
            .whereType<_Slot>()
            .where(
              (slot) =>
                  !slot.time.isBefore(current) && !slot.time.isAfter(horizon),
            )
            .toList()
          ..sort((a, b) => a.time.compareTo(b.time));

    return WeatherOperationType.values
        .map((operation) => _planOperation(operation, slots))
        .toList();
  }

  WeatherOperationPlan _planOperation(
    WeatherOperationType operation,
    List<_Slot> slots,
  ) {
    if (slots.isEmpty) {
      return WeatherOperationPlan(
        operation: operation,
        isSuitable: false,
        score: 0,
        reasonCodes: const ['forecast_unavailable'],
      );
    }

    final evaluations =
        slots.map((slot) => _evaluate(operation, slot)).toList();
    final suitable = evaluations.where((item) => item.score >= 70).toList();
    final pool = suitable.isEmpty ? evaluations : suitable;
    pool.sort((a, b) {
      final score = b.score.compareTo(a.score);
      return score != 0 ? score : a.slot.time.compareTo(b.slot.time);
    });
    final best = pool.first;
    final originalIndex = evaluations.indexOf(best);
    var end = best.slot.time.add(const Duration(hours: 3));
    if (best.score >= 70) {
      for (var index = originalIndex + 1; index < evaluations.length; index++) {
        final next = evaluations[index];
        if (next.score < 70 || next.slot.time.isAfter(end)) break;
        end = next.slot.time.add(const Duration(hours: 3));
      }
    }

    return WeatherOperationPlan(
      operation: operation,
      isSuitable: best.score >= 70,
      score: best.score,
      startsAt: best.slot.time,
      endsAt: end,
      reasonCodes:
          best.reasons.isEmpty ? const ['conditions_acceptable'] : best.reasons,
    );
  }

  _Evaluation _evaluate(WeatherOperationType operation, _Slot slot) {
    var score = 100;
    final reasons = <String>[];

    void penalize(bool condition, int value, String reason) {
      if (!condition) return;
      score -= value;
      reasons.add(reason);
    }

    switch (operation) {
      case WeatherOperationType.spraying:
        penalize(slot.wind >= 8, 75, 'wind_blocking');
        penalize(slot.wind >= 5 && slot.wind < 8, 30, 'wind_elevated');
        penalize(slot.rainProbability >= 0.6, 75, 'rain_probability_blocking');
        penalize(
          slot.rainProbability >= 0.3 && slot.rainProbability < 0.6,
          30,
          'rain_probability_elevated',
        );
        penalize(slot.precipitationMm >= 0.5, 55, 'rain_expected');
        penalize(
          slot.temperature < 5 || slot.temperature > 30,
          25,
          'temperature_risk',
        );
      case WeatherOperationType.irrigation:
        penalize(slot.rainProbability >= 0.6, 60, 'rain_probability_blocking');
        penalize(slot.precipitationMm >= 5, 65, 'rain_expected');
        penalize(slot.temperature >= 35, 25, 'heat_evaporation');
        penalize(slot.wind >= 8, 25, 'wind_elevated');
      case WeatherOperationType.fertilizing:
        penalize(slot.wind >= 8, 65, 'wind_blocking');
        penalize(slot.rainProbability >= 0.7, 55, 'rain_probability_blocking');
        penalize(slot.precipitationMm >= 10, 70, 'heavy_rain_expected');
        penalize(slot.temperature >= 35, 25, 'temperature_risk');
      case WeatherOperationType.harvest:
        penalize(slot.precipitationMm >= 1, 70, 'rain_expected');
        penalize(slot.rainProbability >= 0.6, 55, 'rain_probability_blocking');
        penalize(slot.humidity >= 85, 50, 'humidity_high');
        penalize(
          slot.humidity >= 70 && slot.humidity < 85,
          25,
          'humidity_elevated',
        );
        penalize(slot.wind >= 12, 55, 'wind_blocking');
      case WeatherOperationType.machinery:
        penalize(slot.precipitationMm >= 5, 70, 'heavy_rain_expected');
        penalize(slot.rainProbability >= 0.7, 45, 'rain_probability_blocking');
        penalize(slot.wind >= 12, 55, 'wind_blocking');
        penalize(slot.temperature >= 40, 35, 'temperature_risk');
    }

    return _Evaluation(
      slot: slot,
      score: score.clamp(0, 100).toInt(),
      reasons: reasons,
    );
  }
}

class _Evaluation {
  const _Evaluation({
    required this.slot,
    required this.score,
    required this.reasons,
  });

  final _Slot slot;
  final int score;
  final List<String> reasons;
}

class _Slot {
  const _Slot({
    required this.time,
    required this.temperature,
    required this.humidity,
    required this.wind,
    required this.precipitationMm,
    required this.rainProbability,
  });

  final DateTime time;
  final double temperature;
  final double humidity;
  final double wind;
  final double precipitationMm;
  final double rainProbability;

  static _Slot? fromForecast(WeatherForecastModel value) {
    final time = DateTime.tryParse(value.forecastTime)?.toLocal();
    if (time == null) return null;
    final probability =
        double.tryParse(value.precipitationProbability ?? '') ?? 0;
    return _Slot(
      time: time,
      temperature: double.tryParse(value.temperatureC ?? '') ?? 20,
      humidity: double.tryParse(value.humidityPercent ?? '') ?? 50,
      wind: double.tryParse(value.windSpeedMps ?? '') ?? 0,
      precipitationMm: double.tryParse(value.precipitationMm ?? '') ?? 0,
      rainProbability: probability > 1 ? probability / 100 : probability,
    );
  }
}
