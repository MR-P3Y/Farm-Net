import 'package:go_router/go_router.dart';

import '../../features/activity/presentation/activity_center_screen.dart';
import '../../features/auth/presentation/auth_gate.dart';
import '../../features/consultants/presentation/consultant_detail_screen.dart';
import '../../features/consultants/presentation/consultant_list_screen.dart';
import '../../features/consultants/presentation/consultant_request_create_screen.dart';
import '../../features/consultants/presentation/consultant_workbench_screen.dart';
import '../../features/consultants/presentation/consultation_request_detail_screen.dart';
import '../../features/consultants/presentation/my_consultant_profile_screen.dart';
import '../../features/consultants/presentation/my_consultation_requests_screen.dart';
import '../../features/home/home_screen.dart';
import '../../features/finance/presentation/finance_center_screen.dart';
import '../../features/notifications/presentation/notifications_screen.dart';
import '../../features/notifications/presentation/notification_preferences_screen.dart';
import '../../features/orders/presentation/cart_screen.dart';
import '../../features/orders/presentation/my_orders_screen.dart';
import '../../features/orders/presentation/order_detail_screen.dart';
import '../../features/products/presentation/my_products_screen.dart';
import '../../features/products/presentation/public_product_detail_screen.dart';
import '../../features/products/presentation/public_products_screen.dart';
import '../../features/products/presentation/store_products_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/rentals/presentation/rental_equipment_detail_screen.dart';
import '../../features/rentals/presentation/rental_equipment_list_screen.dart';
import '../../features/rentals/presentation/my_rental_requests_screen.dart';
import '../../features/rentals/presentation/rental_request_create_screen.dart';
import '../../features/rentals/presentation/rental_request_detail_screen.dart';
import '../../features/rentals/presentation/my_lessor_profile_screen.dart';
import '../../features/rentals/presentation/my_rental_equipment_screen.dart';
import '../../features/rentals/presentation/rental_equipment_edit_screen.dart';
import '../../features/rentals/presentation/rental_commercial_screen.dart';
import '../../features/rentals/presentation/rental_workbench_screen.dart';
import '../../features/rentals/presentation/rental_workbench_detail_screen.dart';
import '../../features/rentals/data/rental_models.dart';
import '../../features/social/presentation/social_create_post_screen.dart';
import '../../features/social/presentation/social_feed_screen.dart';
import '../../features/social/presentation/social_post_detail_screen.dart';
import '../../features/search/presentation/unified_search_screen.dart';
import '../../features/services/presentation/service_detail_screen.dart';
import '../../features/services/presentation/service_list_screen.dart';
import '../../features/services/presentation/my_service_requests_screen.dart';
import '../../features/services/presentation/my_offers_screen.dart';
import '../../features/services/presentation/my_provider_profile_screen.dart';
import '../../features/services/presentation/offer_edit_screen.dart';
import '../../features/services/data/service_models.dart';
import '../../features/services/presentation/service_request_create_screen.dart';
import '../../features/services/presentation/service_request_detail_screen.dart';
import '../../features/services/presentation/service_workbench_screen.dart';
import '../../features/services/presentation/service_workbench_detail_screen.dart';
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
      path: '/activity',
      name: 'my-activity-center',
      builder: (context, state) => const ActivityCenterScreen(),
    ),
    GoRoute(
      path: '/search',
      name: 'unified-search',
      builder: (context, state) => const UnifiedSearchScreen(),
    ),
    GoRoute(
      path: '/finance',
      name: 'finance-center',
      builder: (context, state) => const FinanceCenterScreen(),
    ),
    GoRoute(
      path: '/notifications',
      name: 'notifications',
      builder: (context, state) => const NotificationsScreen(),
    ),
    GoRoute(
      path: '/notifications/preferences',
      name: 'notification-preferences',
      builder: (context, state) => const NotificationPreferencesScreen(),
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
      path: '/services',
      name: 'services',
      builder: (context, state) => const ServiceListScreen(),
    ),
    GoRoute(
      path: '/rentals',
      name: 'rental-equipment',
      builder: (context, state) => const RentalEquipmentListScreen(),
    ),
    GoRoute(
      path: '/rentals/equipment/:equipmentId',
      name: 'rental-equipment-detail',
      builder:
          (context, state) => RentalEquipmentDetailScreen(
            equipmentId:
                int.tryParse(state.pathParameters['equipmentId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/rentals/equipment/:equipmentId/request',
      name: 'rental-request-create',
      builder:
          (context, state) => RentalRequestCreateScreen(
            equipmentId:
                int.tryParse(state.pathParameters['equipmentId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/rentals/requests',
      name: 'my-rental-requests',
      builder: (context, state) => const MyRentalRequestsScreen(),
    ),
    GoRoute(
      path: '/rentals/requests/:requestId',
      name: 'rental-request-detail',
      builder:
          (context, state) => RentalRequestDetailScreen(
            requestId:
                int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/rentals/me/lessor-profile',
      builder: (context, state) => const MyLessorProfileScreen(),
    ),
    GoRoute(
      path: '/rentals/me/equipment',
      builder: (context, state) => const MyRentalEquipmentScreen(),
    ),
    GoRoute(
      path: '/rentals/me/equipment/new',
      builder: (context, state) => const RentalEquipmentEditScreen(),
    ),
    GoRoute(
      path: '/rentals/me/equipment/:equipmentId/edit',
      builder:
          (context, state) => RentalEquipmentEditScreen(
            equipment: state.extra as RentalEquipmentOwner?,
          ),
    ),
    GoRoute(
      path: '/rentals/me/equipment/:equipmentId/commercial',
      builder:
          (context, state) => RentalCommercialScreen(
            equipmentId:
                int.tryParse(state.pathParameters['equipmentId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/rentals/workbench',
      builder: (context, state) => const RentalWorkbenchScreen(),
    ),
    GoRoute(
      path: '/rentals/workbench/requests/:requestId',
      builder:
          (context, state) => RentalWorkbenchDetailScreen(
            requestId:
                int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/services/workbench',
      name: 'service-workbench',
      builder: (context, state) => const ServiceWorkbenchScreen(),
    ),
    GoRoute(
      path: '/services/workbench/requests/:requestId',
      name: 'service-workbench-request-detail',
      builder:
          (context, state) => ServiceWorkbenchDetailScreen(
            requestId:
                int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/services/me/provider-profile',
      name: 'my-service-provider-profile',
      builder: (context, state) => const MyProviderProfileScreen(),
    ),
    GoRoute(
      path: '/services/me/offers',
      name: 'my-service-offers',
      builder: (context, state) => const MyOffersScreen(),
    ),
    GoRoute(
      path: '/services/me/offers/new',
      name: 'new-service-offer',
      builder: (context, state) => const OfferEditScreen(),
    ),
    GoRoute(
      path: '/services/me/offers/:offerId/edit',
      name: 'edit-service-offer',
      builder:
          (context, state) =>
              OfferEditScreen(offer: state.extra as ServiceOfferOwner?),
    ),
    GoRoute(
      path: '/services/requests',
      name: 'my-service-requests',
      builder: (context, state) => const MyServiceRequestsScreen(),
    ),
    GoRoute(
      path: '/services/requests/:requestId',
      name: 'service-request-detail',
      builder:
          (context, state) => ServiceRequestDetailScreen(
            requestId:
                int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/services/:offerId/request',
      name: 'service-request-create',
      builder:
          (context, state) => ServiceRequestCreateScreen(
            offerId: int.tryParse(state.pathParameters['offerId'] ?? '') ?? 0,
          ),
    ),
    GoRoute(
      path: '/services/:offerId',
      name: 'service-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['offerId'] ?? '') ?? 0;
        return ServiceDetailScreen(offerId: id);
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
      path: '/consultants/requests/:requestId',
      name: 'consultation-request-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0;
        return ConsultationRequestDetailScreen(
          requestId: id,
          assignedMode: false,
        );
      },
    ),
    GoRoute(
      path: '/consultants/me/profile',
      name: 'my-consultant-profile',
      builder: (context, state) => const MyConsultantProfileScreen(),
    ),
    GoRoute(
      path: '/consultants/workbench',
      name: 'consultant-workbench',
      builder: (context, state) => const ConsultantWorkbenchScreen(),
    ),
    GoRoute(
      path: '/consultants/workbench/requests/:requestId',
      name: 'consultant-workbench-request-detail',
      builder: (context, state) {
        final id = int.tryParse(state.pathParameters['requestId'] ?? '') ?? 0;
        return ConsultationRequestDetailScreen(
          requestId: id,
          assignedMode: true,
        );
      },
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
