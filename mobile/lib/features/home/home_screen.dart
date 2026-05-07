import 'package:flutter/material.dart';

import '../../core/localization/app_localizations.dart';
import '../../core/responsive/responsive.dart';
import '../../core/utils/dates.dart';
import '../../core/widgets/farm_app_bar.dart';
import '../../core/widgets/farm_price_text.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: FarmAppBar(
        title: l10n.appName,
        showBack: false,
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
              child: Padding(
                padding: r.pagePadding(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      l10n.welcome,
                      style: Theme.of(context).textTheme.headlineSmall,
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: r.v(24)),
                    const FarmPriceText(amountToman: 250000),
                    SizedBox(height: r.v(12)),
                    Text(
                      formatJalaliDate(DateTime.now()),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}