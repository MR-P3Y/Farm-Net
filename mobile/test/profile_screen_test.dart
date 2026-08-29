import 'package:farm_net/core/localization/app_localizations.dart';
import 'package:farm_net/core/storage/token_storage.dart';
import 'package:farm_net/core/theme/app_theme.dart';
import 'package:farm_net/features/auth/data/auth_api.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:farm_net/features/auth/data/auth_repository.dart';
import 'package:farm_net/features/auth/state/auth_controller.dart';
import 'package:farm_net/features/auth/state/auth_state.dart';
import 'package:farm_net/features/geo/data/geo_api.dart';
import 'package:farm_net/features/geo/data/geo_models.dart';
import 'package:farm_net/features/geo/data/geo_repository.dart';
import 'package:farm_net/features/profile/data/profile_api.dart';
import 'package:farm_net/features/profile/data/profile_models.dart';
import 'package:farm_net/features/profile/data/profile_repository.dart';
import 'package:farm_net/features/profile/presentation/edit_profile_screen.dart';
import 'package:farm_net/features/profile/presentation/profile_screen.dart';
import 'package:farm_net/features/profile/state/profile_controller.dart';
import 'package:farm_net/features/profile/state/profile_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_test/flutter_test.dart';

const _profile = UserProfile(
  id: 1,
  userId: 7,
  firstName: 'علی',
  lastName: 'کشاورز',
  displayName: 'کشاورز نمونه',
  nationalId: '1234567890',
  birthDate: null,
  gender: null,
  provinceId: 1,
  countyId: 2,
  cityId: 3,
  address: 'نشانی مزرعه',
  postalCode: '0987654321',
  bio: 'تولیدکننده محصول سالم',
  profileCompleted: true,
);

const _user = AuthUser(
  id: 7,
  email: 'farmer@example.com',
  status: 'active',
  isEmailVerified: true,
  isPhoneVerified: false,
  roles: ['user'],
  permissions: [],
);

void main() {
  testWidgets('profile renders account state and masks National ID', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('fa'),
        profileState: const ProfileState(
          isLoading: false,
          profile: _profile,
          provinces: [GeoProvince(id: 1, name: 'فارس')],
          counties: [GeoCounty(id: 2, provinceId: 1, name: 'شیراز')],
          cities: [GeoCity(id: 3, name: 'شیراز')],
        ),
        child: const ProfileScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('کشاورز نمونه'), findsWidgets);
    expect(find.text('farmer@example.com'), findsOneWidget);
    expect(find.text('تأییدشده'), findsOneWidget);
    expect(find.text('••••••۷۸۹۰'), findsOneWidget);
    expect(find.text('1234567890'), findsNothing);
    expect(find.text('خروج از حساب'), findsOneWidget);
  });

  testWidgets('profile load failure has a dedicated retry state', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('en'),
        profileState: const ProfileState(
          isLoading: false,
          errorMessage: 'Could not load profile.',
        ),
        child: const ProfileScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Could not load your profile.'), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
    expect(find.textContaining('not complete'), findsNothing);
  });

  testWidgets('English editor has no fabricated birth date or gender', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('en'),
        profileState: const ProfileState(
          isLoading: false,
          profile: _profile,
          provinces: [GeoProvince(id: 1, name: 'Fars')],
          counties: [GeoCounty(id: 2, provinceId: 1, name: 'Shiraz')],
          cities: [GeoCity(id: 3, name: 'Shiraz')],
        ),
        child: const EditProfileScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Edit profile'), findsOneWidget);
    expect(find.text('Date of birth'), findsOneWidget);
    expect(find.text('Not selected'), findsOneWidget);
    expect(find.text('Prefer not to say'), findsOneWidget);
    expect(find.text('1995-01-01'), findsNothing);
    expect(find.textContaining('میلادی فعلاً'), findsNothing);
  });

  testWidgets('Persian editor explains National ID account conflicts', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('fa'),
        profileState: const ProfileState(
          isLoading: false,
          profile: _profile,
          provinces: [GeoProvince(id: 1, name: 'فارس')],
          counties: [GeoCounty(id: 2, provinceId: 1, name: 'شیراز')],
          cities: [GeoCity(id: 3, name: 'شیراز')],
          errorCode: 'PROFILE_NATIONAL_ID_CONFLICT',
          errorMessage: 'National ID is already linked to another account',
          errorDetails: {'field': 'national_id'},
          errorTraceId: 'profile-trace-id',
        ),
        child: const EditProfileScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.textContaining('این کد ملی قبلاً برای حساب دیگری ثبت شده است'),
      findsOneWidget,
    );
    expect(find.text('شناسه پیگیری: profile-trace-id'), findsOneWidget);
  });

  testWidgets('profile saving shows progress and locks duplicate submission', (
    tester,
  ) async {
    await tester.pumpWidget(
      _testApp(
        locale: const Locale('fa'),
        profileState: const ProfileState(
          isLoading: false,
          isSaving: true,
          profile: _profile,
          provinces: [GeoProvince(id: 1, name: 'فارس')],
          counties: [GeoCounty(id: 2, provinceId: 1, name: 'شیراز')],
          cities: [GeoCity(id: 3, name: 'شیراز')],
        ),
        child: const EditProfileScreen(),
      ),
    );
    await tester.pump();

    expect(find.text('در حال ذخیره تغییرات…'), findsOneWidget);
    expect(
      find.byKey(const Key('farm-primary-action-progress')),
      findsOneWidget,
    );
    expect(find.byKey(const Key('profile-save-progress')), findsOneWidget);
    expect(
      tester
          .widget<AbsorbPointer>(find.byKey(const Key('profile-saving-lock')))
          .absorbing,
      isTrue,
    );
  });
}

Widget _testApp({
  required Locale locale,
  required ProfileState profileState,
  required Widget child,
}) {
  return ProviderScope(
    overrides: [
      profileControllerProvider.overrideWith(
        (ref) => _TestProfileController(profileState),
      ),
      authControllerProvider.overrideWith(
        (ref) => _TestAuthController(
          const AuthState(isLoading: false, isAuthenticated: true, user: _user),
        ),
      ),
    ],
    child: ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      splitScreenMode: true,
      builder:
          (context, _) => MaterialApp(
            locale: locale,
            theme: AppTheme.light(locale),
            darkTheme: AppTheme.dark(locale),
            supportedLocales: AppLocalizations.supportedLocales,
            localizationsDelegates: const [
              AppLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            home: child,
          ),
    ),
  );
}

class _TestProfileController extends ProfileController {
  _TestProfileController(ProfileState initial)
    : super(
        profileRepository: ProfileRepository(api: ProfileApi()),
        geoRepository: GeoRepository(api: GeoApi()),
      ) {
    state = initial;
  }

  @override
  Future<void> load() async {}
}

class _TestAuthController extends AuthController {
  _TestAuthController(AuthState initial)
    : super(
        repository: AuthRepository(
          api: AuthApi(),
          tokenStorage: TokenStorage(),
        ),
      ) {
    state = initial;
  }

  @override
  Future<void> loadCurrentUser() async {}
}
