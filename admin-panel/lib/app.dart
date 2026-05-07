import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import 'core/localization/admin_locale_controller.dart';
import 'core/localization/admin_localizations.dart';
import 'core/routing/admin_router.dart';
import 'core/theme/admin_theme.dart';

class FarmNetAdminApp extends ConsumerWidget {
  const FarmNetAdminApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(adminLocaleControllerProvider);

    return ScreenUtilInit(
      designSize: const Size(1440, 900),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp.router(
          debugShowCheckedModeBanner: false,
          title: 'Farm Net Admin',
          theme: AdminTheme.light,
          darkTheme: AdminTheme.dark,
          themeMode: ThemeMode.system,
          locale: locale,
          supportedLocales: AdminLocalizations.supportedLocales,
          localizationsDelegates: const [
            AdminLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          routerConfig: adminRouter,
        );
      },
    );
  }
}
