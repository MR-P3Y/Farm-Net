import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../../core/localization/app_localizations.dart';
import '../../../../core/utils/digits.dart';
import '../../../../core/widgets/farm_glass_card.dart';
import '../../data/weather_models.dart';
import '../../domain/weather_chart_data.dart';

class WeatherForecastCharts extends StatefulWidget {
  const WeatherForecastCharts({
    required this.forecasts,
    required this.current,
    super.key,
  });

  final List<WeatherForecastModel> forecasts;
  final WeatherSnapshotModel? current;

  @override
  State<WeatherForecastCharts> createState() => _WeatherForecastChartsState();
}

class _WeatherForecastChartsState extends State<WeatherForecastCharts> {
  _ChartKind _selected = _ChartKind.temperature;

  @override
  Widget build(BuildContext context) {
    final data = WeatherChartData.fromForecasts(widget.forecasts);
    if (data.points.length < 2) return const SizedBox.shrink();
    final specification = _specification(context, _selected);
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 28, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    context.l10n.tr(
                      fa: 'روند ۲۴ ساعت آینده',
                      en: 'Next 24-hour trends',
                    ),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ),
                Text(
                  context.l10n.tr(
                    fa: 'داده واقعی پیش‌بینی',
                    en: 'Forecast data',
                  ),
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.58),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children:
                  _ChartKind.values.map((kind) {
                    final selected = kind == _selected;
                    final spec = _specification(context, kind);
                    return Padding(
                      padding: const EdgeInsetsDirectional.only(end: 8),
                      child: Semantics(
                        button: true,
                        selected: selected,
                        label: spec.label,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(18),
                          onTap: () => setState(() => _selected = kind),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 180),
                            constraints: const BoxConstraints(minHeight: 42),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 13,
                              vertical: 9,
                            ),
                            decoration: BoxDecoration(
                              color:
                                  selected
                                      ? Color.alphaBlend(
                                        spec.color.withValues(alpha: 0.48),
                                        const Color(0xB3303840),
                                      )
                                      : const Color(0x99303840),
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(
                                color:
                                    selected
                                        ? spec.color.withValues(alpha: 0.95)
                                        : Colors.white.withValues(alpha: 0.32),
                              ),
                              boxShadow:
                                  selected
                                      ? [
                                        BoxShadow(
                                          color: spec.color.withValues(
                                            alpha: 0.2,
                                          ),
                                          blurRadius: 10,
                                        ),
                                      ]
                                      : null,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(spec.icon, size: 17, color: Colors.white),
                                const SizedBox(width: 6),
                                Text(
                                  spec.label,
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                    fontWeight:
                                        selected
                                            ? FontWeight.w900
                                            : FontWeight.w600,
                                  ),
                                ),
                                if (selected) ...[
                                  const SizedBox(width: 6),
                                  const Icon(
                                    Icons.check_circle_rounded,
                                    color: Colors.white,
                                    size: 15,
                                  ),
                                ],
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
            ),
          ),
          const SizedBox(height: 10),
          FarmGlassCard(
            borderRadius: 26,
            opacity: 0.1,
            padding: const EdgeInsets.fromLTRB(14, 16, 14, 12),
            child: Column(
              children: [
                SizedBox(
                  height: 190,
                  width: double.infinity,
                  child: CustomPaint(
                    painter: _WeatherLineChartPainter(
                      points: data.points,
                      values: data.points.map(specification.value).toList(),
                      color: specification.color,
                      unit: specification.unit,
                      isFa: context.l10n.isFa,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(
                      Icons.schedule_rounded,
                      color: Colors.white60,
                      size: 15,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        context.l10n.tr(
                          fa: 'نقاط نمودار بر اساس زمان واقعی هر Forecast هستند.',
                          en:
                              'Chart points use each forecast row’s real timestamp.',
                        ),
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.62),
                          fontSize: 10,
                        ),
                      ),
                    ),
                    if (_selected == _ChartKind.wind &&
                        widget.current?.windDirectionDeg != null)
                      _WindDirectionBadge(
                        degrees: widget.current!.windDirectionDeg!,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

enum _ChartKind { temperature, rain, humidity, wind }

class _ChartSpecification {
  const _ChartSpecification({
    required this.label,
    required this.unit,
    required this.icon,
    required this.color,
    required this.value,
  });

  final String label;
  final String unit;
  final IconData icon;
  final Color color;
  final double? Function(WeatherChartPoint) value;
}

_ChartSpecification _specification(BuildContext context, _ChartKind kind) =>
    switch (kind) {
      _ChartKind.temperature => _ChartSpecification(
        label: context.l10n.tr(fa: 'دما', en: 'Temperature'),
        unit: '°C',
        icon: Icons.thermostat_rounded,
        color: Colors.orangeAccent,
        value: (point) => point.temperature,
      ),
      _ChartKind.rain => _ChartSpecification(
        label: context.l10n.tr(fa: 'احتمال بارش', en: 'Rain chance'),
        unit: '%',
        icon: Icons.water_drop_outlined,
        color: const Color(0xFF64B5F6),
        value: (point) => point.rainProbability,
      ),
      _ChartKind.humidity => _ChartSpecification(
        label: context.l10n.tr(fa: 'رطوبت', en: 'Humidity'),
        unit: '%',
        icon: Icons.opacity_rounded,
        color: const Color(0xFF80CBC4),
        value: (point) => point.humidity,
      ),
      _ChartKind.wind => _ChartSpecification(
        label: context.l10n.tr(fa: 'سرعت باد', en: 'Wind speed'),
        unit: 'm/s',
        icon: Icons.air_rounded,
        color: const Color(0xFFCE93D8),
        value: (point) => point.windSpeed,
      ),
    };

class _WindDirectionBadge extends StatelessWidget {
  const _WindDirectionBadge({required this.degrees});

  final int degrees;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Transform.rotate(
            angle: degrees * math.pi / 180,
            child: const Icon(
              Icons.navigation_rounded,
              color: Colors.white,
              size: 14,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            context.l10n.isFa
                ? '${toPersianDigits(degrees)}° فعلی'
                : '$degrees° now',
            style: const TextStyle(color: Colors.white70, fontSize: 9),
          ),
        ],
      ),
    );
  }
}

class _WeatherLineChartPainter extends CustomPainter {
  _WeatherLineChartPainter({
    required this.points,
    required this.values,
    required this.color,
    required this.unit,
    required this.isFa,
  });

  final List<WeatherChartPoint> points;
  final List<double?> values;
  final Color color;
  final String unit;
  final bool isFa;

  @override
  void paint(Canvas canvas, Size size) {
    const left = 42.0;
    const top = 14.0;
    const bottom = 28.0;
    final chart = Rect.fromLTRB(
      left,
      top,
      size.width - 8,
      size.height - bottom,
    );
    final usable = values.whereType<double>().toList();
    if (usable.length < 2 || chart.width <= 0) return;
    var minValue = usable.reduce(math.min);
    var maxValue = usable.reduce(math.max);
    if ((maxValue - minValue).abs() < 0.01) {
      minValue -= 1;
      maxValue += 1;
    }
    final gridPaint =
        Paint()
          ..color = Colors.white.withValues(alpha: 0.12)
          ..strokeWidth = 1;
    for (var line = 0; line <= 3; line++) {
      final y = chart.top + chart.height * line / 3;
      canvas.drawLine(Offset(chart.left, y), Offset(chart.right, y), gridPaint);
      final value = maxValue - (maxValue - minValue) * line / 3;
      _text(
        canvas,
        '${value.toStringAsFixed(value.abs() < 10 ? 1 : 0)}$unit',
        Offset(0, y - 7),
      );
    }
    final path = Path();
    final fill = Path();
    var started = false;
    Offset? first;
    Offset? last;
    for (var index = 0; index < values.length; index++) {
      final value = values[index];
      if (value == null) continue;
      final x =
          chart.left + chart.width * index / math.max(1, values.length - 1);
      final y =
          chart.bottom -
          chart.height * (value - minValue) / (maxValue - minValue);
      final point = Offset(x, y);
      if (!started) {
        path.moveTo(x, y);
        first = point;
        started = true;
      } else {
        path.lineTo(x, y);
      }
      last = point;
    }
    if (first == null || last == null) return;
    fill
      ..moveTo(first.dx, chart.bottom)
      ..lineTo(first.dx, first.dy)
      ..addPath(path, Offset.zero)
      ..lineTo(last.dx, chart.bottom)
      ..close();
    canvas.drawPath(
      fill,
      Paint()
        ..shader = LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            color.withValues(alpha: 0.35),
            color.withValues(alpha: 0.01),
          ],
        ).createShader(chart),
    );
    canvas.drawPath(
      path,
      Paint()
        ..color = color
        ..strokeWidth = 2.5
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
    final labelIndexes = <int>{0, values.length ~/ 2, values.length - 1};
    for (final index in labelIndexes) {
      final x =
          chart.left + chart.width * index / math.max(1, values.length - 1);
      final raw = '${points[index].time.hour.toString().padLeft(2, '0')}:00';
      final label = isFa ? toPersianDigits(raw) : raw;
      _text(canvas, label, Offset(x - 16, chart.bottom + 8));
    }
  }

  void _text(Canvas canvas, String value, Offset offset) {
    final painter = TextPainter(
      text: TextSpan(
        text: isFa ? toPersianDigits(value) : value,
        style: const TextStyle(color: Colors.white60, fontSize: 9),
      ),
      textDirection: isFa ? TextDirection.rtl : TextDirection.ltr,
    )..layout();
    painter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant _WeatherLineChartPainter oldDelegate) =>
      oldDelegate.values != values ||
      oldDelegate.color != color ||
      oldDelegate.isFa != isFa;
}
