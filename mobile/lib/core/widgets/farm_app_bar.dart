import 'package:flutter/material.dart';

import 'farm_back_button.dart';

class FarmAppBar extends StatelessWidget implements PreferredSizeWidget {
  const FarmAppBar({
    super.key,
    required this.title,
    this.actions,
    this.showBack = true,
  });

  final String title;
  final List<Widget>? actions;
  final bool showBack;

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    final canPop = Navigator.canPop(context);

    return AppBar(
      centerTitle: true,
      title: Text(title),
      leading: showBack && canPop ? const FarmBackButton() : null,
      actions: actions,
    );
  }
}
