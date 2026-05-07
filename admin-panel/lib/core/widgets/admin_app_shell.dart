import 'package:flutter/material.dart';

import '../responsive/admin_responsive.dart';
import 'admin_sidebar.dart';
import 'admin_topbar.dart';

class AdminAppShell extends StatelessWidget {
  const AdminAppShell({
    super.key,
    required this.child,
  });

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AdminResponsiveBuilder(
        builder: (context, constraints, r) {
          return Row(
            children: [
              SizedBox(
                width: r.sidebarWidth(),
                child: const AdminSidebar(),
              ),
              Expanded(
                child: Column(
                  children: [
                    const AdminTopbar(),
                    Expanded(child: child),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
