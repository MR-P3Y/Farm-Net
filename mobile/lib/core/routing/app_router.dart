import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/auth_gate.dart';
import '../../features/consultants/presentation/consultant_detail_screen.dart';
import '../../features/consultants/presentation/consultant_list_screen.dart';
import '../../features/consultants/presentation/consultant_request_create_screen.dart';
import '../../features/consultants/presentation/my_consultant_profile_screen.dart';
import '../../features/consultants/presentation/my_consultation_requests_screen.dart';
import '../../features/home/home_screen.dart';
import '../../features/notifications/presentation/notifications_screen.dart';
import '../../features/orders/presentation/cart_screen.dart';
import '../../features/orders/presentation/my_orders_screen.dart';
import '../../features/orders/presentation/order_detail_screen.dart';
import '../../features/products/presentation/my_products_screen.dart';
import '../../features/products/presentation/public_product_detail_screen.dart';
import '../../features/products/presentation/public_products_screen.dart';
import '../../features/products/presentation/store_products_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/social/presentation/social_create_post_screen.dart';
import '../../features/social/presentation/social_feed_screen.dart';
import '../../features/social/presentation/social_post_detail_screen.dart';
import '../../features/splash/splash_screen.dart';
import '../../features/stores/presentation/my_store_screen.dart';
import '../../features/stores/presentation/public_store_detail_screen.dart';
import '../../features/stores/presentation/public_stores_screen.dart';
import '../../features/verification/presentation/verification_requests_screen.dart';
import '../../features/weather/presentation/weather_screen.dart';

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
      path: '/notifications',
      name: 'notifications',
      builder: (context, state) => const NotificationsScreen(),
    ),
    GoRoute(
      path: '/weather',
      name: 'weather',
      builder: (context, state) => const WeatherScreen(),
    ),
    GoRoute(
      path: '/social',
      name: 'social',
      builder: (context, state) => const SocialFeedScreen(),
    ),
    GoRoute(
      path: '/social/create',
      name: 'social-create',
      builder: (context, state) => const SocialCreatePostScreen(),
    ),
    GoRoute(
      path: '/social/detail/:id',
      name: 'social-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['id'] ?? '') ?? 0;
        return SocialPostDetailScreen(postId: id);
      },
    ),
    GoRoute(
      path: '/consultants',
      name: 'consultants',
      builder: (context, state) => const ConsultantListScreen(),
    ),
    GoRoute(
      path: '/consultants/requests',
      name: 'my-consultation-requests',
      builder: (context, state) => const MyConsultationRequestsScreen(),
    ),
    GoRoute(
      path: '/consultants/me/profile',
      name: 'my-consultant-profile',
      builder: (context, state) => const MyConsultantProfileScreen(),
    ),
    GoRoute(
      path: '/consultants/:profileId/request',
      name: 'consultant-request-create',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['profileId'] ?? '') ?? 0;
        return ConsultantRequestCreateScreen(consultantProfileId: id);
      },
    ),
    GoRoute(
      path: '/consultants/:profileId',
      name: 'consultant-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['profileId'] ?? '') ?? 0;
        return ConsultantDetailScreen(profileId: id);
      },
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
      path: '/products',
      name: 'public-products',
      builder: (context, state) => const PublicProductsScreen(),
    ),
    GoRoute(
      path: '/products/:productId',
      name: 'public-product-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['productId'] ?? '') ?? 0;
        return PublicProductDetailScreen(productId: id);
      },
    ),
    GoRoute(
      path: '/cart',
      name: 'cart',
      builder: (context, state) => const CartScreen(),
    ),
    GoRoute(
      path: '/orders',
      name: 'my-orders',
      builder: (context, state) => const MyOrdersScreen(),
    ),
    GoRoute(
      path: '/orders/:orderId',
      name: 'order-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['orderId'] ?? '') ?? 0;
        return OrderDetailScreen(orderId: id);
      },
    ),
    GoRoute(
      path: '/stores/:storeSlug/products',
      name: 'store-products',
      builder: (context, state) {
        final storeSlug = state.pathParameters['storeSlug'] ?? '';
        return StoreProductsScreen(storeSlug: storeSlug);
      },
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
      path: '/my-products',
      name: 'my-products',
      builder: (context, state) => const MyProductsScreen(),
    ),
    GoRoute(
      path: '/splash',
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
  ],
);
