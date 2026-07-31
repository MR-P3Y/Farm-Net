import 'package:flutter/widgets.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class AppBreakpoints {
  const AppBreakpoints._();

  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;
}

class ResponsiveBuilder extends StatelessWidget {
  const ResponsiveBuilder({super.key, required this.builder});

  final Widget Function(BuildContext context, BoxConstraints constraints, R r)
  builder;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return builder(context, constraints, R(context, constraints));
      },
    );
  }
}

class R {
  R(this.context, this.constraints);

  final BuildContext context;
  final BoxConstraints constraints;

  Size get size => MediaQuery.sizeOf(context);

  double get width => constraints.maxWidth;
  double get height => constraints.maxHeight;

  bool get isMobile => width < AppBreakpoints.mobile;
  bool get isTablet =>
      width >= AppBreakpoints.mobile && width < AppBreakpoints.tablet;
  bool get isDesktop => width >= AppBreakpoints.tablet;

  double s(double value) => value.w;

  double v(double value) => value.h;

  double sp(double value) => value.sp;

  EdgeInsets pagePadding() {
    if (isDesktop) {
      return EdgeInsets.symmetric(horizontal: s(32), vertical: v(24));
    }

    if (isTablet) {
      return EdgeInsets.symmetric(horizontal: s(24), vertical: v(20));
    }

    return EdgeInsets.symmetric(horizontal: s(16), vertical: v(16));
  }

  double maxContentWidth() {
    if (isDesktop) return 1100;
    if (isTablet) return 760;
    return width;
  }
}

extension ContextMediaX on BuildContext {
  Size get mediaSize => MediaQuery.sizeOf(this);
  bool get isRtl => Directionality.of(this) == TextDirection.rtl;
}
