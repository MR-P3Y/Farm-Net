import 'package:flutter/material.dart';

import '../../core/localization/admin_localizations.dart';

class AdminForbiddenPage extends StatelessWidget {
  const AdminForbiddenPage({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AdminLocalizations.of(context);

    return Center(
      child: Text(
        l10n.forbidden,
        style: Theme.of(context).textTheme.headlineSmall,
      ),
    );
  }
}
