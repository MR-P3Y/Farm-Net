import 'package:flutter/widgets.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class AdminBreakpoints {
  const AdminBreakpoints._();

  static const double compact = 900;
  static const double wide = 1200;
}

class AdminResponsiveBuilder extends StatelessWidget {
  const AdminResponsiveBuilder({
    super.key,
    required this.builder,
  });

  final Widget Function(
    BuildContext context,
    BoxConstraints constraints,
    AdminR r,
  ) builder;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return builder(context, constraints, AdminR(context, constraints));
      },
    );
  }
}

class AdminR {
  AdminR(this.context, this.constraints);

  final BuildContext context;
  final BoxConstraints constraints;

  double get width => constraints.maxWidth;
  double get height => constraints.maxHeight;

  bool get isCompact => width < AdminBreakpoints.compact;
  bool get isWide => width >= AdminBreakpoints.wide;

  double s(double value) => value.w;
  double v(double value) => value.h;
  double sp(double value) => value.sp;

  double sidebarWidth() => isCompact ? 76 : 260;

  EdgeInsets pagePadding() {
    return EdgeInsets.symmetric(
      horizontal: isCompact ? s(16) : s(24),
      vertical: v(20),
    );
  }
}
