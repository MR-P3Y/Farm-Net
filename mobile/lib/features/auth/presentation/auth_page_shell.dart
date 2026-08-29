import 'package:flutter/material.dart';

import '../../../core/responsive/responsive.dart';

/// Shared full-screen authentication layout.
///
/// Android keeps its normal `adjustResize` contract. The background fills the
/// current Flutter viewport, the form owns the scroll area, and an optional
/// action panel stays outside that scroll area without manual keyboard insets.
class AuthPageShell extends StatelessWidget {
  const AuthPageShell({
    required this.child,
    super.key,
    this.bottomPanel,
    this.maxWidth = 400,
    this.mobileHorizontalPadding = 24,
    this.mobileAlignment = const Alignment(0, -0.45),
    this.desktopAlignment = AlignmentDirectional.centerEnd,
    this.layoutKey,
    this.backgroundKey,
  });

  final Widget child;
  final Widget? bottomPanel;
  final double maxWidth;
  final double mobileHorizontalPadding;
  final Alignment mobileAlignment;
  final AlignmentGeometry desktopAlignment;
  final Key? layoutKey;
  final Key? backgroundKey;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7F1),
      resizeToAvoidBottomInset: true,
      body: ResponsiveBuilder(
        builder: (context, constraints, responsive) {
          final isWide = responsive.width > 900;
          final backgroundImage =
              responsive.isDesktop
                  ? 'assets/images/login_bg_web.webp'
                  : responsive.isTablet
                  ? 'assets/images/login_bg_tablet.webp'
                  : 'assets/images/login_bg_mobile.webp';
          final horizontalPadding =
              isWide
                  ? EdgeInsets.symmetric(horizontal: responsive.width * .08)
                  : EdgeInsets.symmetric(horizontal: mobileHorizontalPadding);

          Widget constrained(Widget content) {
            return Align(
              alignment:
                  isWide ? desktopAlignment : AlignmentDirectional.center,
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: maxWidth),
                child: content,
              ),
            );
          }

          return Stack(
            key: layoutKey,
            fit: StackFit.expand,
            children: [
              Image.asset(
                key: backgroundKey,
                backgroundImage,
                fit: BoxFit.cover,
                alignment: isWide ? Alignment.centerLeft : Alignment.center,
              ),
              ColoredBox(color: Colors.black.withValues(alpha: .15)),
              SafeArea(
                child: Padding(
                  padding: horizontalPadding,
                  child: Column(
                    children: [
                      Expanded(
                        child: LayoutBuilder(
                          builder: (context, viewport) {
                            return SingleChildScrollView(
                              keyboardDismissBehavior:
                                  ScrollViewKeyboardDismissBehavior.onDrag,
                              physics: const BouncingScrollPhysics(),
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              child: ConstrainedBox(
                                constraints: BoxConstraints(
                                  minHeight: viewport.maxHeight - 16,
                                ),
                                child: Align(
                                  alignment:
                                      isWide
                                          ? Alignment.center
                                          : mobileAlignment,
                                  child: constrained(child),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                      if (bottomPanel != null) ...[
                        const SizedBox(height: 8),
                        constrained(bottomPanel!),
                        const SizedBox(height: 8),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
