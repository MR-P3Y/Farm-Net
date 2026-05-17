import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/auth_gate.dart';
import '../../features/home/home_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/splash/splash_screen.dart';
import '../../features/stores/presentation/my_store_screen.dart';
import '../../features/stores/presentation/public_store_detail_screen.dart';
import '../../features/stores/presentation/public_stores_screen.dart';
import '../../features/verification/presentation/verification_requests_screen.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'auth-gate',
      builder: (context, state) => const AuthGate(),
    ),
    GoRoute(
      path: '/home',
      name: 'home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/profile',
      name: 'profile',
      builder: (context, state) => const ProfileScreen(),
    ),
    GoRoute(
      path: '/verifications',
      name: 'verifications',
      builder: (context, state) => const VerificationRequestsScreen(),
    ),
    GoRoute(
      path: '/stores',
      name: 'public-stores',
      builder: (context, state) => const PublicStoresScreen(),
    ),
    GoRoute(
      path: '/stores/:slug',
      name: 'public-store-detail',
      builder: (context, state) {
        final slug = state.pathParameters['slug'] ?? '';
        return PublicStoreDetailScreen(slug: slug);
      },
    ),
    GoRoute(
      path: '/my-store',
      name: 'my-store',
      builder: (context, state) => const MyStoreScreen(),
    ),
    GoRoute(
      path: '/splash',
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
  ],
);
